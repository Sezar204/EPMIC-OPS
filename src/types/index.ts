export interface ApiResponse<T> {
  success: boolean
  data: T
  message: string
  total?: number
  page?: number
  page_size?: number
  errors?: { field: string; message: string }[]
}

export interface Factory {
  id: number
  code: string
  name: string
  type: "b2b" | "b2c" | "hybrid"
  status: "active" | "inactive" | "maintenance"
  location?: string
  currency: string
  timezone: string
  working_start: string
  working_end: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface FactoryHealthScore {
  factory_id: number
  total_score: number
  plan_adherence: number
  machine_availability: number
  quality_rate: number
  inventory_health: number
  order_fulfillment: number
  workforce_stability: number
  status: "excellent" | "good" | "warning" | "critical"
}

export interface ProductionLine {
  id: number
  factory_id: number
  code: string
  name: string
  type: "discrete" | "process" | "batch"
  capacity_per_hour: number
  capacity_unit: string
  status: "active" | "idle" | "maintenance" | "down"
  changeover_minutes: number
  notes?: string
  created_at: string
  updated_at: string
}

export interface Machine {
  id: number
  factory_id: number
  line_id?: number
  code: string
  name: string
  type?: string
  capacity?: number
  capacity_unit?: string
  criticality: "low" | "medium" | "high" | "critical"
  status: "active" | "idle" | "maintenance" | "down"
  purchase_date?: string
  warranty_expiry?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface Shift {
  id: number
  factory_id: number
  name: string
  start_time: string
  end_time: string
  break_minutes: number
  days_of_week: number[]
  headcount: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Product {
  id: number
  factory_id: number
  sku: string
  name: string
  category?: string
  unit_of_measure: string
  standard_cost: number
  selling_price: number
  min_order_qty: number
  lead_time_days: number
  shelf_life_days?: number
  type: "finished" | "semi-finished"
  notes?: string
  created_at: string
  updated_at: string
}

export interface BOMHeader {
  id: number
  factory_id: number
  product_id: number
  version: string
  name: string
  status: "active" | "inactive" | "draft"
  yield_pct: number
  effective_date?: string
  notes?: string
  lines?: BOMLine[]
  product?: Product
  created_at: string
  updated_at: string
}

export interface BOMLine {
  id: number
  bom_id: number
  material_id: number
  quantity_required: number
  unit: string
  loss_factor_pct: number
  is_alternative: boolean
  alt_material_id?: number
  sequence_no: number
  notes?: string
  material_name?: string
  material_code?: string
}

export interface RawMaterial {
  id: number
  factory_id: number
  code: string
  name: string
  category?: string
  unit_of_measure: string
  standard_cost: number
  safety_stock_qty: number
  reorder_point_qty: number
  lead_time_days: number
  shelf_life_days?: number
  storage_conditions?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface InventoryItem {
  id: number
  factory_id: number
  material_id?: number
  product_id?: number
  warehouse_id?: number
  qty_on_hand: number
  qty_reserved: number
  qty_available: number
  batch_number?: string
  expiry_date?: string
  last_updated: string
  days_coverage?: number
  coverage_status?: "critical" | "warning" | "ok"
  material?: RawMaterial
  product?: Product
}

export interface Customer {
  id: number
  factory_id: number
  code: string
  name: string
  type: "b2b" | "b2c" | "distributor"
  priority: number
  credit_limit?: number
  payment_terms_days?: number
  contact_name?: string
  contact_email?: string
  contact_phone?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface SalesOrder {
  id: number
  factory_id: number
  customer_id: number
  order_number: string
  order_date: string
  required_delivery: string
  confirmed_delivery?: string
  status: "draft"|"confirmed"|"in_production"|"ready"|"shipped"|"delivered"|"cancelled"
  total_value: number
  currency: string
  is_rush_order: boolean
  priority: number
  notes?: string
  lines?: SalesOrderLine[]
  customer?: Customer
  created_at: string
  updated_at: string
}

export interface SalesOrderLine {
  id: number
  order_id: number
  product_id: number
  quantity: number
  unit_price: number
  discount_pct: number
  line_total: number
  required_date?: string
  committed_date?: string
  status: string
  fulfilled_qty: number
  notes?: string
  product?: Product
}

export interface Supplier {
  id: number
  factory_id: number
  code: string
  name: string
  contact_name?: string
  contact_email?: string
  contact_phone?: string
  payment_terms_days?: number
  rating: number
  status: "active" | "inactive" | "blacklisted"
  notes?: string
  created_at: string
  updated_at: string
}

export interface PurchaseOrder {
  id: number
  factory_id: number
  supplier_id: number
  po_number: string
  order_date: string
  expected_delivery: string
  actual_delivery?: string
  status: "planned"|"issued"|"confirmed"|"in_transit"|"received"|"closed"|"cancelled"
  total_value: number
  currency: string
  notes?: string
  lines?: PurchaseOrderLine[]
  supplier?: Supplier
  created_at: string
  updated_at: string
}

export interface PurchaseOrderLine {
  id: number
  po_id: number
  material_id: number
  qty_ordered: number
  unit_price: number
  qty_received?: number
  quality_status: "pending" | "accepted" | "rejected"
  notes?: string
  material?: RawMaterial
}

export interface Alert {
  id: number
  factory_id: number
  alert_type: string
  severity: "info" | "warning" | "critical" | "emergency"
  title: string
  message?: string
  source_module?: string
  source_id?: number
  is_read: boolean
  is_resolved: boolean
  created_at: string
  resolved_at?: string
}

export interface Decision {
  id: number
  factory_id: number
  decision_type: string
  title: string
  description?: string
  recommendation?: string
  impact_summary?: Record<string, string>
  status: "pending" | "approved" | "modified" | "rejected"
  priority: "low" | "medium" | "high" | "urgent"
  created_at: string
  decided_at?: string
  decision_notes?: string
}

export interface KPIDefinition {
  id: number
  factory_id?: number
  code: string
  name: string
  category: string
  formula?: string
  unit?: string
  target_value?: number
  warning_threshold?: number
  critical_threshold?: number
  higher_is_better: boolean
  is_custom: boolean
  display_format: "number" | "percentage" | "currency"
  is_active: boolean
}

export interface KPIValue {
  id: number
  kpi_id: number
  factory_id: number
  period_type: string
  period_date: string
  value: number
  status: "good" | "warning" | "critical"
  calculated_at: string
  kpi?: KPIDefinition
  trend?: number[]
}

export interface BackupInfo {
  filename: string
  backup_type: "auto" | "manual" | "scheduled"
  file_size_bytes: number
  created_at: string
  status: "success" | "failed"
  file_path: string
}

export interface Worker {
  id: number
  factory_id: number
  employee_id: string
  name: string
  department?: string
  role?: string
  skills?: string[]
  status: "active" | "inactive" | "on_leave"
  notes?: string
  created_at: string
  updated_at: string
}

export interface QualityCheck {
  id: number
  factory_id: number
  check_type: "iqc" | "ipqc" | "oqc"
  reference_id?: number
  reference_type?: string
  product_id?: number
  material_id?: number
  status: "pending" | "passed" | "failed" | "on_hold"
  checked_at?: string
  sample_size: number
  defects_found: number
  defect_rate_pct: number
  decision?: string
  notes?: string
  created_at: string
}

export interface MaintenanceWorkOrder {
  id: number
  factory_id: number
  machine_id: number
  wo_number: string
  type: "preventive" | "corrective" | "emergency"
  status: "created" | "assigned" | "in_progress" | "completed" | "cancelled"
  priority: "low" | "medium" | "high" | "critical"
  description?: string
  assigned_to?: string
  created_at: string
  started_at?: string
  completed_at?: string
  downtime_hours: number
  root_cause?: string
  resolution?: string
}

export interface Warehouse {
  id: number
  factory_id: number
  code: string
  name: string
  type: "raw_material" | "wip" | "finished_goods" | "general"
  total_capacity: number
  capacity_unit: string
  storage_conditions?: string
  location?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface PaginationParams {
  page?: number
  page_size?: number
  search?: string
  sort_by?: string
  sort_order?: "asc" | "desc"
}
