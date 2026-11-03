import { useCallback, useEffect, useState } from 'react'

function validResponse(data, page, pageSize) {
  return Boolean(
    data && Array.isArray(data.items)
    && Number.isInteger(data.total) && data.total >= data.items.length
    && data.items.length <= pageSize
    && data.page === page && data.page_size === pageSize
    && data.items.every((item) => (
      item && typeof item.id === 'string' && typeof item.title === 'string'
    )),
  )
}

export default function useCursos({ pageSize = 20 } = {}) {
  const size = Number.isInteger(pageSize) && pageSize >= 1 && pageSize <= 100
    ? pageSize : 20
  const [query, setQuery] = useState({
    page: 1, filters: { q: '', category_id: '' }, revision: 0,
  })
  const [loaded, setLoaded] = useState(null)
  const page = query.page
  const params = new URLSearchParams({ page: String(page), page_size: String(size) })
  if (query.filters.q) params.set('q', query.filters.q)
  if (query.filters.category_id) params.set('category_id', query.filters.category_id)
  const requestUrl = `/api/v1/courses?${params.toString()}`
  const requestKey = JSON.stringify([requestUrl, query.revision])

  useEffect(() => {
    const controller = new AbortController()
    let active = true

    async function load() {
      try {
        const response = await fetch(requestUrl, { signal: controller.signal })
        if (!response.ok) throw new Error('COURSES_REQUEST_FAILED')
        const data = await response.json()
        if (!validResponse(data, page, size)) throw new Error('COURSES_RESPONSE_INVALID')
        if (active && !controller.signal.aborted) {
          setLoaded({ key: requestKey, cursos: data.items, total: data.total, error: false })
        }
      } catch {
        if (active && !controller.signal.aborted) {
          setLoaded({ key: requestKey, cursos: [], total: 0, error: true })
        }
      }
    }

    load()
    return () => {
      active = false
      controller.abort()
    }
  }, [requestUrl, requestKey, page, size])

  const setPage = useCallback((nextPage) => {
    if (!Number.isInteger(nextPage) || nextPage < 1) return
    setQuery((previous) => (
      previous.page === nextPage ? previous : { ...previous, page: nextPage }
    ))
  }, [])

  const setFilters = useCallback((patch) => {
    if (!patch || typeof patch !== 'object' || Array.isArray(patch)) return
    setQuery((previous) => {
      const merged = { ...previous.filters, ...patch }
      const filters = {
        q: typeof merged.q === 'string' ? merged.q.trim() : '',
        category_id: typeof merged.category_id === 'string' ? merged.category_id.trim() : '',
      }
      if (
        filters.q === previous.filters.q
        && filters.category_id === previous.filters.category_id
      ) return previous
      return { ...previous, page: 1, filters }
    })
  }, [])

  const refetch = useCallback(() => {
    setQuery((previous) => ({ ...previous, revision: previous.revision + 1 }))
  }, [])

  const current = loaded?.key === requestKey
  return {
    loading: !current,
    error: current ? loaded.error : false,
    cursos: current ? loaded.cursos : [],
    total: current ? loaded.total : 0,
    page, pageSize: size, filters: query.filters,
    setPage, setFilters, refetch,
  }
}
