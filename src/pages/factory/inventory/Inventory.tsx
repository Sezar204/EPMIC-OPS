Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { Package, AlertTriangle, TrendingUp, BarChart3 } from "lucide-react"
import { inventoryApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { Table } from "@/components/ui/Table"
import { PageSkeleton } from "@/components/ui/PageSkeleton"
import { ColumnDef } from "@tanstack/react-table"

export default function Inventory() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
