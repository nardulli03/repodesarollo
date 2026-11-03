import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.{js,jsx}'],
    clearMocks: true,
    restoreMocks: true,
    coverage: {
      provider: 'v8',
      include: ['src/features/catalogo/hooks/useCursos.js'],
      reporter: ['text', 'html'],
      reportsDirectory: 'coverage',
    },
  },
})
