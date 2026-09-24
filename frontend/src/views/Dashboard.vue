<template>
  <section class="page">
    <header class="page-head">
      <div>
        <h2>运营概览</h2>
        <p class="page-desc">汇总各业务模块的关键指标，先看总量再看异常。</p>
      </div>
      <div class="page-actions">
        <button class="btn" type="button" :disabled="loading" @click="reload">
          {{ loading ? '刷新中…' : '刷新' }}
        </button>
      </div>
    </header>

    <p v-if="errorMessage" class="overview-banner error-text" role="alert">
      <span>
        {{ errorMessage }}<template v-if="stale">；当前展示的是上次成功获取的数据（更新于 {{ updatedAt }}）</template>
      </span>
      <button class="btn primary" type="button" :disabled="loading" @click="reload">重试</button>
    </p>

    <div class="stat-row">
      <article v-for="card in cards" :key="card.label" class="stat-card">
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
      </article>
    </div>

    <table class="data-table">
      <thead>
        <tr><th>业务模块</th><th>记录总量</th><th>今日新增</th><th>待处理</th><th>异常量</th></tr>
      </thead>
      <tbody>
        <tr v-for="row in moduleRows" :key="row.name">
          <td>{{ row.name }}</td>
          <td>{{ row.total }}</td>
          <td>{{ row.created }}</td>
          <td>{{ row.pending }}</td>
          <td>{{ row.abnormal }}</td>
        </tr>
        <tr v-if="loading && !moduleRows.length">
          <td colspan="5" class="empty-state">概览数据加载中…</td>
        </tr>
        <tr v-if="!loading && !moduleRows.length">
          <td colspan="5" class="empty-state">暂无概览数据，所有指标按零值展示</td>
        </tr>
      </tbody>
    </table>

    <footer class="page-foot">
      <span>共 {{ moduleRows.length }} 个业务模块，记录总量与各模块列表页的总数一致</span>
      <span v-if="updatedAt">数据更新于 {{ updatedAt }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { fetchJson } from '@/api/client'

type Card = { label: string; value: number }
type ModuleRow = { name: string; total: number; created: number; pending: number; abnormal: number }
type Overview = {
  generated_at?: string
  cards: Card[]
  modules: ModuleRow[]
}

const CARD_LABELS = ['业务模块', '记录总量', '今日新增', '待处理', '异常量'] as const
const CACHE_KEY = 'overview:last-success'

const zeroCards = (): Card[] => CARD_LABELS.map((label) => ({ label, value: 0 }))

const cards = ref<Card[]>(zeroCards())
const moduleRows = ref<ModuleRow[]>([])
const loading = ref(false)
const errorMessage = ref('')
const updatedAt = ref('')
const stale = ref(false)

function asCount(value: unknown): number {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

/** 后端缺字段或返回空时统一补零，避免卡片/单元格渲染成空白。 */
function normalizeOverview(payload: Partial<Overview> | null): Overview {
  const rawCards = Array.isArray(payload?.cards) ? payload!.cards! : []
  const byLabel = new Map<string, number>(
    rawCards
      .filter((card) => card && typeof card.label === 'string')
      .map((card) => [card.label, asCount(card.value)]),
  )
  const normalizedCards: Card[] = CARD_LABELS.map((label) => ({
    label,
    value: byLabel.get(label) ?? 0,
  }))
  const normalizedModules: ModuleRow[] = Array.isArray(payload?.modules)
    ? payload!.modules!
        .filter((row) => row && typeof row.name === 'string')
        .map((row) => ({
          name: row.name,
          total: asCount(row.total),
          created: asCount(row.created),
          pending: asCount(row.pending),
          abnormal: asCount(row.abnormal),
        }))
    : []
  return {
    generated_at: typeof payload?.generated_at === 'string' ? payload.generated_at : '',
    cards: normalizedCards,
    modules: normalizedModules,
  }
}

function applyOverview(data: Overview, at: string) {
  cards.value = data.cards
  moduleRows.value = data.modules
  updatedAt.value = at
}

function readCache(): { data: Overview; at: string } | null {
  try {
    const raw = window.sessionStorage.getItem(CACHE_KEY)
    if (!raw) {
      return null
    }
    const parsed = JSON.parse(raw) as { at?: string; payload?: Partial<Overview> }
    if (!parsed.at || !parsed.payload) {
      return null
    }
    return { data: normalizeOverview(parsed.payload), at: parsed.at }
  } catch {
    return null
  }
}

function writeCache(data: Overview, at: string) {
  try {
    window.sessionStorage.setItem(CACHE_KEY, JSON.stringify({ at, payload: data }))
  } catch {
    // 缓存写不进（隐私模式/容量满）不影响页面展示，忽略即可
  }
}

async function reload() {
  loading.value = true
  errorMessage.value = ''
  try {
    const payload = await fetchJson<Overview>('/api/overview')
    const data = normalizeOverview(payload)
    const at = new Date().toLocaleString()
    applyOverview(data, at)
    writeCache(data, at)
    stale.value = false
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : '概览接口异常，请稍后重试'
    // 失败不清空已有数据：还保留着上次成功结果时，说明当前数据已过期
    stale.value = moduleRows.value.length > 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 首次加载先还原本会话上次成功的数据，避免接口失败时整页空白
  const cached = readCache()
  if (cached) {
    applyOverview(cached.data, cached.at)
  }
  void reload()
})
</script>

<style scoped>
.overview-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 0 0 12px;
  padding: 8px 12px;
  border: 1px solid currentColor;
  border-radius: 6px;
  font-size: 13px;
}
.btn[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
