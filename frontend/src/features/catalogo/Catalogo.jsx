import { useEffect, useState } from 'react'

export default function Catalogo() {
  const [estado, setEstado] = useState({
    loading: true,
    error: false,
    cursos: [],
  })

  useEffect(() => {
    const controller = new AbortController()

    async function cargarCursos() {
      try {
        const response = await fetch('/api/v1/courses', {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error('Error al consultar cursos')
        }

        const data = await response.json()

        if (!Array.isArray(data.items)) {
          throw new Error('Respuesta inesperada')
        }

        if (!controller.signal.aborted) {
          setEstado({
            loading: false,
            error: false,
            cursos: data.items,
          })
        }
      } catch {
        if (!controller.signal.aborted) {
          setEstado({
            loading: false,
            error: true,
            cursos: [],
          })
        }
      }
    }

    cargarCursos()

    return () => controller.abort()
  }, [])

  return (
    <main className="contenedor">
      <h1>Cursos Abiertos</h1>
      <p>Descubrí cursos gratuitos para seguir aprendiendo.</p>

      {estado.loading && (
        <p role="status">Cargando cursos…</p>
      )}

      {estado.error && (
        <div role="alert">
          <p>No pudimos cargar los cursos.</p>
          <button onClick={() => window.location.reload()}>
            Reintentar
          </button>
        </div>
      )}

      {!estado.loading && !estado.error && (
        estado.cursos.length === 0 ? (
          <p>Todavía no hay cursos publicados.</p>
        ) : (
          <ul className="cursos">
            {estado.cursos.map((curso) => (
              <li key={curso.id}>
                <h2>{curso.title}</h2>
              </li>
            ))}
          </ul>
        )
      )}
    </main>
  )
}