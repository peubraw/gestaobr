import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, MapPin, Users, Globe, Building2, Clock, Map, Activity } from 'lucide-react';
import { getEstado, formatNum } from '@/lib/api';
import MunicipiosLista from '@/components/MunicipiosLista';

export const dynamic = 'force-dynamic';

const REGIAO_COLORS: Record<string, string> = {
  'Norte': 'border-l-emerald-500',
  'Nordeste': 'border-l-orange-500',
  'Centro-Oeste': 'border-l-purple-500',
  'Sudeste': 'border-l-blue-500',
  'Sul': 'border-l-red-500',
};

const REGIAO_BG: Record<string, string> = {
  'Norte': 'bg-emerald-100 text-emerald-800',
  'Nordeste': 'bg-orange-100 text-orange-800',
  'Centro-Oeste': 'bg-purple-100 text-purple-800',
  'Sudeste': 'bg-blue-100 text-blue-800',
  'Sul': 'bg-red-100 text-red-800',
};

function KpiCard({ title, value, unit, icon: Icon }: { title: string; value: string; unit?: string; icon: React.ElementType }) {
  return (
    <div className="bg-white border-b-4 border-gov-blue p-3 flex flex-col justify-between shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest font-mono">{title}</span>
        <Icon size={14} className="text-gov-blue" />
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-xl font-bold font-mono text-gov-dark">{value}</span>
        {unit && <span className="text-xs font-mono text-gray-500 mb-0.5">{unit}</span>}
      </div>
    </div>
  );
}

export default async function EstadoPage({ params }: { params: Promise<{ uf: string }> }) {
  const { uf } = await params;

  let estado;
  try {
    estado = await getEstado(uf);
  } catch {
    notFound();
  }

  const regiaoColor = REGIAO_COLORS[estado.regiao] ?? 'border-l-gray-400';
  const regiaoBg = REGIAO_BG[estado.regiao] ?? 'bg-gray-100 text-gray-700';

  return (
    <div className="flex flex-col gap-6">
      {/* Top Status Bar */}
      <div className="flex flex-wrap items-center justify-between text-xs border-b border-gray-300 pb-2">
        <nav className="flex items-center gap-2 text-gray-500 font-mono">
          <Link href="/gestaobr" className="hover:text-gov-blue flex items-center gap-1">
            <ArrowLeft size={14} /> INÍCIO
          </Link>
          <span>/</span>
          <span className="text-gov-dark font-bold">PAINEL ESTADUAL</span>
        </nav>
        <div className="flex items-center gap-4 font-mono">
          <span className="flex items-center gap-1 text-gov-green font-bold">
            <span className="w-2 h-2 rounded-full bg-gov-green animate-pulse"></span>
            DADOS SINCRONIZADOS
          </span>
          <span className="text-gray-400 flex items-center gap-1"><Clock size={12} /> REF: 2024</span>
        </div>
      </div>

      {/* Header */}
      <section className={`bg-gray-100 border border-gov-border border-l-8 ${regiaoColor} p-4 shadow-inner`}>
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6 mb-4">
          <div>
            <div className="flex items-center gap-3 mb-1 flex-wrap">
              <h1 className="text-4xl font-black text-gov-dark uppercase tracking-tight">{estado.nome}</h1>
              <span className="bg-gov-dark text-white font-mono font-bold px-3 py-1 text-lg">{estado.uf}</span>
              <span className={`text-xs font-mono font-bold px-2 py-1 rounded ${regiaoBg}`}>
                {estado.regiao}
              </span>
            </div>
            <p className="text-gov-blue font-mono font-bold flex items-center gap-2">
              <MapPin size={14} /> Capital: {estado.capital}
            </p>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <KpiCard title="Municípios" value={estado.n_municipios.toString()} icon={Building2} />
          <KpiCard title="População" value={formatNum(estado.populacao)} unit="hab" icon={Users} />
          <KpiCard title="Região" value={estado.regiao} icon={Map} />
          <KpiCard title="Capital" value={estado.capital} icon={Activity} />
        </div>
      </section>

      {/* Municipalities section */}
      <section className="mc-card">
        <div className="mc-header">
          <Globe size={16} className="text-gov-yellow" />
          Municípios de {estado.nome}
        </div>
        <MunicipiosLista municipios={estado.municipios} uf={estado.uf} />
      </section>
    </div>
  );
}
