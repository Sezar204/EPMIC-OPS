Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { Calendar, Plus, RefreshCw } from "lucide-react"
import { productionApi, productionLinesApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { BarChart } from "@/components/charts"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function ProductionPlanning() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const [tab, setTab] = useState("daily")
