import { act, cleanup, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import useCursos from './useCursos.js'

const courses = [{ id: 'curso-1', title: 'Introducción a Python' }]

function deferred() {
  let resolve
  const promise = new Promise((done) => { resolve = done })
  return { promise, resolve }
}

function response(items = courses, metadata = {}) {
  return {
    ok: true,
    json: vi.fn().mockResolvedValue({
      items, total: items.length, page: 1, page_size: 20, ...metadata,
    }),
  }
}

function requestedParams() {
  const [url] = fetch.mock.lastCall
  return new URL(url, 'http://localhost').searchParams
}

function respondToPage(url) {
  const params = new URL(url, 'http://localhost').searchParams
  return Promise.resolve(response(courses, {
    page: Number(params.get('page')),
    page_size: Number(params.get('page_size')),
    total: 100,
  }))
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn())
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('useCursos', () => {
  it('mantiene loading mientras la petición está pendiente', async () => {
    // Arrange
    const request = deferred()
    fetch.mockReturnValue(request.promise)
    // Act
    const { result } = renderHook(() => useCursos())
    // Assert
    expect(result.current.loading).toBe(true)
    expect(result.current.cursos).toEqual([])
    await act(async () => { request.resolve(response()) })
    await waitFor(() => expect(result.current.loading).toBe(false))
  })

  it('expone los cursos y el total al completar la carga', async () => {
    // Arrange
    fetch.mockResolvedValue(response(courses, { total: 5 }))
    // Act
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(result.current.cursos).toEqual(courses)
    expect(result.current.total).toBe(5)
    expect(result.current.error).toBe(false)
    expect(requestedParams().get('page')).toBe('1')
    expect(requestedParams().get('page_size')).toBe('20')
  })

  it('expone error y lista vacía cuando falla la red', async () => {
    // Arrange
    fetch.mockRejectedValue(new TypeError('Network error'))
    // Act
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(result.current.error).toBe(true)
    expect(result.current.cursos).toEqual([])
    expect(result.current.total).toBe(0)
  })

  it.each([404, 500])('trata HTTP %i como error', async (status) => {
    // Arrange
    fetch.mockResolvedValue({ ok: false, status })
    // Act
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(result.current.error).toBe(true)
    expect(result.current.cursos).toEqual([])
  })

  it.each([
    { items: null, total: 0, page: 1, page_size: 20 },
    { items: [], total: '0', page: 1, page_size: 20 },
    { items: [], total: -1, page: 1, page_size: 20 },
    { items: [null], total: 1, page: 1, page_size: 20 },
    { items: [], total: 0, page: 2, page_size: 20 },
  ])('rechaza un contrato de respuesta inválido %#', async (body) => {
    // Arrange
    fetch.mockResolvedValue({ ok: true, json: vi.fn().mockResolvedValue(body) })
    // Act
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(result.current.error).toBe(true)
    expect(result.current.cursos).toEqual([])
  })

  it('maneja una respuesta cuyo JSON no puede leerse', async () => {
    // Arrange
    fetch.mockResolvedValue({ ok: true, json: vi.fn().mockRejectedValue(new SyntaxError('JSON inválido')) })
    // Act
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(result.current.error).toBe(true)
  })

  it('setPage recarga utilizando la página solicitada', async () => {
    // Arrange
    fetch.mockImplementation(respondToPage)
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Act
    act(() => result.current.setPage(2))
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(result.current.page).toBe(2)
    expect(requestedParams().get('page')).toBe('2')
    expect(fetch).toHaveBeenCalledTimes(2)
  })

  it.each([
    { q: 'Python avanzado' },
    { category_id: '00000000-0000-4000-8000-000000000001' },
  ])('cambiar un filtro vuelve a página 1 sin petición intermedia %#', async (filter) => {
    // Arrange
    fetch.mockImplementation(respondToPage)
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.loading).toBe(false))
    act(() => result.current.setPage(3))
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Act
    act(() => result.current.setFilters(filter))
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    const [field, value] = Object.entries(filter)[0]
    expect(result.current.page).toBe(1)
    expect(requestedParams().get('page')).toBe('1')
    expect(requestedParams().get(field)).toBe(value)
    expect(fetch).toHaveBeenCalledTimes(3)
  })

  it('refetch conserva página y filtros actuales', async () => {
    // Arrange
    fetch.mockImplementation(respondToPage)
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.loading).toBe(false))
    act(() => result.current.setFilters({ q: 'python', category_id: 'categoria-1' }))
    await waitFor(() => expect(result.current.loading).toBe(false))
    act(() => result.current.setPage(2))
    await waitFor(() => expect(result.current.loading).toBe(false))
    const [previousUrl] = fetch.mock.lastCall
    const previousCalls = fetch.mock.calls.length
    // Act
    act(() => result.current.refetch())
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(fetch).toHaveBeenCalledTimes(previousCalls + 1)
    expect(fetch.mock.lastCall[0]).toBe(previousUrl)
    expect(result.current.page).toBe(2)
  })

  it('refetch permite recuperarse de un error', async () => {
    // Arrange
    fetch.mockRejectedValueOnce(new TypeError('Sin conexión'))
      .mockResolvedValueOnce(response())
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.error).toBe(true))
    // Act
    act(() => result.current.refetch())
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(result.current.error).toBe(false)
    expect(result.current.cursos).toEqual(courses)
  })

  it('cancela la petición al desmontar el componente', () => {
    // Arrange
    fetch.mockReturnValue(new Promise(() => {}))
    const { unmount } = renderHook(() => useCursos())
    const [, options] = fetch.mock.lastCall
    // Act
    unmount()
    // Assert
    expect(options.signal.aborted).toBe(true)
  })

  it('una respuesta anterior no reemplaza resultados de filtros nuevos', async () => {
    // Arrange
    const oldRequest = deferred()
    const newRequest = deferred()
    fetch.mockReturnValueOnce(oldRequest.promise).mockReturnValueOnce(newRequest.promise)
    const { result } = renderHook(() => useCursos())
    const newCourses = [{ id: 'curso-2', title: 'Nuevo resultado' }]
    // Act
    act(() => result.current.setFilters({ q: 'nuevo' }))
    await act(async () => { newRequest.resolve(response(newCourses)) })
    await waitFor(() => expect(result.current.cursos).toEqual(newCourses))
    await act(async () => { oldRequest.resolve(response(courses)) })
    // Assert
    expect(result.current.cursos).toEqual(newCourses)
    expect(result.current.error).toBe(false)
  })

  it('funciona con la ejecución adicional de efectos de StrictMode', async () => {
    // Arrange
    fetch.mockResolvedValue(response())
    // Act
    const { result } = renderHook(() => useCursos(), { reactStrictMode: true })
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(result.current.cursos).toEqual(courses)
    expect(result.current.error).toBe(false)
  })

  it.each([0, -1, 1.5])('ignora una página inválida: %s', async (page) => {
    // Arrange
    fetch.mockResolvedValue(response())
    const { result } = renderHook(() => useCursos())
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Act
    act(() => result.current.setPage(page))
    // Assert
    expect(result.current.page).toBe(1)
    expect(fetch).toHaveBeenCalledTimes(1)
  })

  it('permite configurar el tamaño de página', async () => {
    // Arrange
    fetch.mockResolvedValue(response(courses, { page_size: 5 }))
    // Act
    const { result } = renderHook(() => useCursos({ pageSize: 5 }))
    await waitFor(() => expect(result.current.loading).toBe(false))
    // Assert
    expect(requestedParams().get('page_size')).toBe('5')
    expect(result.current.pageSize).toBe(5)
    expect(result.current.error).toBe(false)
  })
})
