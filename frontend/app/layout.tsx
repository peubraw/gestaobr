import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'GestãoBR — Painel de Gestão Municipal',
  description: 'Ferramenta de gestão pública para prefeitos e vereadores. Dados de orçamento, indicadores sociais, contratos e câmara municipal.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="bg-gov-gray text-gov-text min-h-screen">
        {/* Barra do governo */}
        <div className="bg-gov-dark text-white text-xs py-1 px-4 flex items-center gap-2">
          <span className="font-bold tracking-wide">GOVERNO FEDERAL</span>
          <span className="text-gray-400">|</span>
          <span className="text-gray-300">Acesso à Informação</span>
        </div>

        {/* Header principal */}
        <header className="bg-gov-blue text-white shadow-md">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div>
                <div className="text-xs font-semibold uppercase tracking-widest text-blue-200">
                  Sistema Nacional
                </div>
                <div className="text-2xl font-bold tracking-tight">GestãoBR</div>
                <div className="text-xs text-blue-200">Painel de Gestão Municipal</div>
              </div>
            </div>
            <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
              <a href="/gestaobr" className="hover:text-blue-200 transition-colors">Início</a>
              <a href="/gestaobr/sobre" className="hover:text-blue-200 transition-colors">Sobre</a>
            </nav>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-8">
          {children}
        </main>

        <footer className="mt-16 border-t border-gov-border bg-white">
          <div className="max-w-7xl mx-auto px-4 py-8 text-sm text-gray-500">
            <div className="flex flex-col md:flex-row justify-between gap-4">
              <div>
                <p className="font-semibold text-gov-dark">GestãoBR</p>
                <p>Dados públicos consolidados para gestores municipais.</p>
              </div>
              <div className="text-right">
                <p>Fontes: IBGE, Tesouro Nacional (SICONFI), Portal da Transparência (CGU)</p>
                <p>BrasilAPI · Dados Abertos Federais</p>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
