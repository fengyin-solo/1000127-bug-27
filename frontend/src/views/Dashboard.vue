<template>
  <section class="page">
    <header class="page-head">
      <div>
        <h2>运营概览</h2>
        <p class="page-desc">汇总各业务模块的关键指标，先看总量再看异常。</p>
      </div>
      <div class="page-actions">
        <button class="btn" type="button" :disabled="loading" @click="loadOverview">
          {{ loading ? '刷新中…' : '刷新数据' }}
        </button>
      </div>
    </header>

    <div v-if="errorMessage" class="inline-alert error" role="alert">
      <span>{{ errorMessage }}</span>
      <button class="link" type="button" :disabled="loading" @click="loadOverview">重试</button>
    </div>

    <div v-if="overview" class="overview-meta">
      <span v-if="stale" class="stale-tag">当前展示的是上次成功数据</span>
      <span>统计日期：{{ overview.date }}</span>
      <span>数据更新于：{{ overview.generated_at }}</span>
    </div>

    <div class="stat-row" v-if="overview" :aria-busy="loading">
      <article v-for="card in overview.cards" :key="card.label" class="stat-card">
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ loading && stale ? '…' : card.value }}</strong>
      </article>
    </div>

    <table class="data-table" v-if="overview">
      <thead>
        <tr><th>业务模块</th><th>今日新增</th><th>记录总量</th><th>待处理</th><th>异常量</th></tr>
      </thead>
      <tbody>
        <tr v-for="row in overview.modules" :key="row.key">
          <td>
            <RouterLink class="link" :to="`/${row.key}`">{{ row.name }}</RouterLink>
          </td>
          <td>{{ row.created }}</td>
          <td>{{ row.total }}</td>
          <td>{{ row.pending }}</td>
          <td :class="{ 'warn-text': row.abnormal > 0 }">{{ row.abnormal }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="loading && !overview" class="state-block">正在加载运营概览…</div>
    <div v-else-if="!loading && !overview" class="state-block">
      <p class="state-text">运营概览暂时无法展示。</p>
      <p class="state-sub">{{ errorMessage }}</p>
      <button class="btn primary" type="button" @click="loadOverview">重新加载</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { fetchJson } from '@/api/client'

type OverviewCard = { label: string; value: number }
type OverviewModule = {
  key: string
  name: string
  total: number
  created: number
  pending: number
  abnormal: number
}
type Overview = {
  cards: OverviewCard[]
  modules: OverviewModule[]
  date: string
  generated_at: string
}

const overview = ref<Overview | null>(null)
const loading = ref(false)
const errorMessage = ref('')
const stale = ref(false)

async function loadOverview() {
  loading.value = true
  errorMessage.value = ''
  try {
    const payload = await fetchJson<Overview>('/api/overview')
    overview.value = normalizeOverview(payload)
    stale.value = false
  } catch (error) {
    // 失败时不清空 overview：保留上一次成功的数据，仅提示原因。
    errorMessage.value = error instanceof Error
      ? `运营概览加载失败：${error.message}`
      : '运营概览加载失败，请稍后重试'
    stale.value = overview.value !== null
  } finally {
    loading.value = false
  }
}

/** 兜底补齐：后端字段缺失或某模块没有任何记录时，也要显示零值而不是空白。 */
function normalizeOverview(payload: Partial<Overview>): Overview {
  const cards = Array.isArray(payload.cards) ? payload.cards : []
  const modules = (Array.isArray(payload.modules) ? payload.modules : []).map((raw) => {
    const item = raw ?? {}
    return {
      key: String(item.key ?? item.name ?? ''),
      name: String(item.name ?? item.key ?? '未命名模块'),
      total: toNumber(item.total),
      created: toNumber(item.created),
      pending: toNumber(item.pending),
      abnormal: toNumber(item.abnormal),
    }
  })
  return {
    cards: cards.map((card) => ({
      label: String(card?.label ?? ''),
      value: toNumber(card?.value),
    })),
    modules,
    date: String(payload.date ?? ''),
    generated_at: String(payload.generated_at ?? ''),
  }
}

function toNumber(value: unknown): number {
  const num = Number(value)
  return Number.isFinite(num) ? num : 0
}

onMounted(loadOverview)
</script>
