import { useState } from 'react'
import useCursos from './hooks/useCursos.js'
import './Catalogo.css'

export default function Catalogo() {
  const {
    loading, error, cursos, total, page, pageSize, filters,
    setPage, setFilters, refetch,
  } = useCursos()
  const [busqueda, setBusqueda] = useState('')
  const ultimaPagina = Math.max(1, Math.ceil(total / pageSize))

  function buscar(event) {
    event.preventDefault()
    setFilters({ q: busqueda })
  }

  return (
    <main className="contenedor">
      <h1>Cursos Abiertos</h1>
      <p>Descubrí cursos gratuitos para seguir aprendiendo.</p>

      <form className="catalogo-busqueda" onSubmit={buscar} role="search">
        <label htmlFor="buscar-cursos">Buscar cursos</label>
        <div className="catalogo-busqueda-controles">
          <input
            id="buscar-cursos"
            name="q"
            type="search"
            maxLength={100}
            placeholder="Título, tema o proveedor"
            value={busqueda}
            onChange={(event) => setBusqueda(event.target.value)}
          />
          <button type="submit">Buscar</button>
        </div>
      </form>

      {loading && <p role="status">Cargando cursos…</p>}

      {error && (
        <div role="alert">
          <p>No pudimos cargar los cursos.</p>
          <button type="button" onClick={refetch}>Reintentar</button>
        </div>
      )}

      {!loading && !error && (
        <>
          {cursos.length === 0 ? (
            <p role="status">
              {filters.q || filters.category_id
                ? 'No encontramos cursos para esta búsqueda.'
                : 'Todavía no hay cursos publicados.'}
            </p>
          ) : (
            <>
              <p role="status">{total} {total === 1 ? 'curso encontrado' : 'cursos encontrados'}.</p>
              <ul className="cursos">
                {cursos.map((curso) => (
                  <li key={curso.id}><h2>{curso.title}</h2></li>
                ))}
              </ul>
            </>
          )}

          {(total > 0 || page > 1) && (
            <nav className="catalogo-paginacion" aria-label="Páginas del catálogo">
              <button type="button" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                Anterior
              </button>
              <span aria-current="page">Página {page}</span>
              <button type="button" disabled={page >= ultimaPagina} onClick={() => setPage(page + 1)}>
                Siguiente
              </button>
            </nav>
          )}
        </>
      )}
    </main>
  )
}
