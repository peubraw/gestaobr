import type { Metadata } from 'next';
import './globals.css';
import { Home, Info, Activity, Shield, Database } from 'lucide-react';

export const metadata: Metadata = {
  title: 'GestãoBR — Painel de Gestão Municipal',
  description: 'Ferramenta de gestão pública para prefeitos e vereadores. Dados de orçamento, indicadores sociais, contratos e câmara municipal.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="bg-gov-gray text-gov-text min-h-screen flex flex-col">
        {/* Barra de status do sistema (Tiny Bar) */}
        <div className="bg-gov-dark text-white text-[10px] uppercase tracking-widest py-1 px-4 flex items-center justify-between border-b border-blue-900">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1"><Shield size={10} className="text-gov-green" /> STATUS: OPERACIONAL</span>
            <span className="flex items-center gap-1"><Database size={10} /> SINC: ATIVO (UTC-3)</span>
          </div>
          <div className="flex items-center gap-4 text-gray-400">
            <span className="hidden md:inline">SISTEMA DE GESTÃO ESTRATÉGICA FEDERAL</span>
            <span className="text-gov-yellow font-bold">NÍVEL DE ACESSO: PÚBLICO</span>
          </div>
        </div>

        {/* Header principal Mission Control */}
        <header className="bg-gov-blue text-white shadow-md border-b-4 border-gov-yellow relative overflow-hidden">
          {/* Background grid effect */}
          <div className="absolute inset-0 opacity-10 bg-[linear-gradient(rgba(255,255,255,0.2)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.2)_1px,transparent_1px)] bg-[size:20px_20px]"></div>
          
          <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col md:flex-row md:items-center justify-between relative z-10 gap-4">
            <div className="flex items-center gap-6">
              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-gov-yellow mb-0.5">
                  Governo Federal — República Federativa do Brasil
                </div>
                <div className="text-2xl font-bold tracking-tight flex items-center gap-2">
                  <Activity size={24} className="text-gov-yellow" />
                  GestãoBR
                </div>
              </div>
              
              {/* Pseudo-breadcrumb para manter o estilo mission control no layout base */}
              <div className="hidden lg:flex items-center gap-2 text-xs font-mono text-blue-200 bg-blue-900/50 px-3 py-1.5 rounded border border-blue-800">
                <span className="text-white font-bold">NODE</span> <span className="text-gray-400">/</span> FEDERAL <span className="text-gray-400">/</span> <span className="text-gov-green flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-gov-green animate-pulse"></span> CONECTADO</span>
              </div>
            </div>
            
            <nav className="flex items-center gap-5 text-sm font-medium">
              <a href="/gestaobr" className="flex items-center gap-1.5 text-blue-100 hover:text-gov-yellow transition-colors"><Home size={16} /> Início</a>
              <a href="/gestaobr/sobre" className="flex items-center gap-1.5 text-blue-100 hover:text-gov-yellow transition-colors"><Info size={16} /> Sobre</a>
            </nav>
          </div>
        </header>

        <main className="max-w-[90rem] w-full mx-auto px-4 py-6 flex-1">
          {children}
        </main>

        <footer className="mt-auto border-t-2 border-gov-border bg-white">
          <div className="max-w-[90rem] mx-auto px-4 py-6 text-sm text-gray-500 font-mono">
            <div className="flex flex-col md:flex-row justify-between gap-4">
              <div>
                <p className="font-bold text-gov-dark uppercase text-xs">GestãoBR - Monitoramento Nacional</p>
                <p className="text-xs">Dados públicos consolidados para inteligência governamental.</p>
              </div>
              <div className="text-right text-xs">
                <p>FONTES HOMOLOGADAS: IBGE | STN (SICONFI) | CGU</p>
                <p>TRANSMISSÃO CRIPTOGRAFADA · DADOS ABERTOS</p>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
