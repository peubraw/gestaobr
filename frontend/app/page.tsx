'use client';

import { useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Search, MapPin, ChevronRight, Building2, Users, FileText, TrendingUp, Globe, Database, Activity, Map } from 'lucide-react';
import { MunicipioBusca } from '@/lib/api';

async function buscarMunicipiosClient(q: string): Promise<MunicipioBusca[]> {
  const base = process.env.NEXT_PUBLIC_API_URL || '/gestaobr/api';
  const r = await fetch(`${base}/municipios/busca?q=${encodeURIComponent(q)}`);
  if (!r.ok) return [];
  return r.json();
}

const UFS = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
  'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<MunicipioBusca[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleInput = useCallback((val: string) => {
    setQuery(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (val.length < 2) { setResults([]); return; }
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      const res = await buscarMunicipiosClient(val);
      setResults(res);
      setLoading(false);
    }, 350);
  }, []);

  const handleSelect = (m: MunicipioBusca) => {
    router.push(`/municipio/${m.codigo_ibge}`);
  };

  return (
    <div className="flex flex-col gap-8 -mt-6 -mx-4 md:-mx-4 lg:-mx-4 xl:-mx-4 2xl:-mx-4">
      {/* Hero Mission Control */}
      <section className="relative bg-gov-dark px-4 py-16 md:py-24 overflow-hidden border-b-8 border-gov-blue">
        {/* Background elements */}
        <div className="absolute inset-0 opacity-20 bg-[linear-gradient(rgba(255,255,255,0.2)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.2)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-gov-blue rounded-full filter blur-[100px] opacity-30 mix-blend-screen pointer-events-none"></div>
        
        <div className="relative z-10 max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-black/30 border border-blue-500/30 text-gov-yellow text-xs font-mono px-4 py-1.5 rounded-sm mb-8 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-gov-green animate-pulse"></span>
            SISTEMA DE MONITORAMENTO NACIONAL INTEGRADO
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 tracking-tight uppercase">
            Painel de Controle <span className="text-gov-yellow">Municipal</span>
          </h1>
          
          <p className="text-blue-100 text-lg md:text-xl max-w-3xl mx-auto mb-12 font-light">
            Plataforma de inteligência governamental. Acesso em tempo real a indicadores sociais, execução orçamentária, composição legislativa e contratos da união.
          </p>

          {/* Search box - Highlighted */}
          <div className="relative max-w-2xl mx-auto mb-12">
            <div className="flex items-center bg-white border-4 border-gov-yellow shadow-[0_0_30px_rgba(255,205,7,0.3)] overflow-visible">
              <Search size={28} className="ml-5 text-gov-blue flex-shrink-0" />
              <input
                type="text"
                placeholder="BUSCAR MUNICÍPIO OU CÓDIGO IBGE..."
                value={query}
                onChange={e => handleInput(e.target.value)}
                className="flex-1 px-5 py-5 text-lg font-bold text-gov-dark placeholder:text-gray-400 uppercase outline-none bg-transparent"
                autoComplete="off"
              />
              {loading && (
                <div className="mr-5 w-6 h-6 border-4 border-gov-blue border-t-transparent rounded-full animate-spin" />
              )}
            </div>

            {/* Dropdown resultados */}
            {results.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gov-dark shadow-2xl z-50 max-h-[400px] overflow-y-auto text-left text-gov-dark font-mono">
                {results.map(m => (
                  <button
                    key={m.codigo_ibge}
                    onClick={() => handleSelect(m)}
                    className="w-full flex items-center gap-4 px-5 py-4 hover:bg-gov-blue hover:text-white transition-colors border-b border-gray-200 last:border-0 group"
                  >
                    <MapPin size={20} className="text-gov-blue group-hover:text-gov-yellow flex-shrink-0" />
                    <span className="flex-1 font-bold text-lg">{m.nome}</span>
                    <span className="text-sm bg-gray-200 text-gray-800 group-hover:bg-blue-800 group-hover:text-white px-2 py-1 rounded font-bold">{m.uf}</span>
                    <span className="text-xs text-gray-500 group-hover:text-blue-300">IBGE: {m.codigo_ibge}</span>
                    <ChevronRight size={20} className="text-gray-400 group-hover:text-white" />
                  </button>
                ))}
              </div>
            )}

            {query.length >= 2 && !loading && results.length === 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-gov-dark border-2 border-red-500 text-red-400 p-4 font-mono shadow-2xl z-50 text-left">
                NENHUM REGISTRO ENCONTRADO PARA "{query.toUpperCase()}"
              </div>
            )}
          </div>
          
          {/* UFs Grid */}
          <div className="max-w-3xl mx-auto">
            <p className="text-xs font-mono text-blue-300 mb-3 tracking-widest flex items-center justify-center gap-2">
              <Map size={14} /> EXPLORAR POR UNIDADE FEDERATIVA
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {UFS.map(uf => (
                <button key={uf} className="bg-white/10 hover:bg-gov-yellow hover:text-gov-dark text-white font-mono font-bold text-xs py-1.5 px-2.5 rounded transition-colors border border-white/20 hover:border-gov-yellow">
                  {uf}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <div className="max-w-[90rem] w-full mx-auto px-4">
        {/* National Stats - Mission Control Style */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 -mt-16 relative z-20">
          <div className="bg-white border-2 border-gov-dark shadow-xl p-6 flex items-center gap-5 border-l-8 border-l-gov-blue">
            <div className="p-4 bg-blue-50 rounded-full text-gov-blue">
              <MapPin size={32} />
            </div>
            <div>
              <div className="text-xs font-bold text-gray-500 font-mono tracking-widest mb-1">MUNICÍPIOS MONITORADOS</div>
              <div className="text-4xl font-black text-gov-dark font-mono">5.570</div>
            </div>
          </div>
          <div className="bg-white border-2 border-gov-dark shadow-xl p-6 flex items-center gap-5 border-l-8 border-l-gov-green">
            <div className="p-4 bg-green-50 rounded-full text-gov-green">
              <Globe size={32} />
            </div>
            <div>
              <div className="text-xs font-bold text-gray-500 font-mono tracking-widest mb-1">UNIDADES FEDERATIVAS</div>
              <div className="text-4xl font-black text-gov-dark font-mono">27</div>
            </div>
          </div>
          <div className="bg-white border-2 border-gov-dark shadow-xl p-6 flex items-center gap-5 border-l-8 border-l-gov-yellow">
            <div className="p-4 bg-yellow-50 rounded-full text-yellow-600">
              <Database size={32} />
            </div>
            <div>
              <div className="text-xs font-bold text-gray-500 font-mono tracking-widest mb-1">ORÇAMENTO CONSOLIDADO</div>
              <div className="text-4xl font-black text-gov-dark font-mono">R$ 1,3T</div>
            </div>
          </div>
        </section>

        {/* Features as Dashboard Modules */}
        <section className="mb-12">
          <h2 className="text-xl font-bold font-mono text-gov-dark mb-6 flex items-center gap-2 border-b-2 border-gray-200 pb-2 uppercase">
            <Activity size={24} className="text-gov-blue" />
            Módulos do Sistema
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: TrendingUp,
                title: 'Indicadores Sociais',
                desc: 'PIB per capita, IDHM, saneamento e educação consolidados.',
                color: 'border-l-blue-500'
              },
              {
                icon: FileText,
                title: 'Execução Financeira',
                desc: 'Receitas e despesas da LOA executada via SICONFI (STN).',
                color: 'border-l-green-500'
              },
              {
                icon: Users,
                title: 'Poder Legislativo',
                desc: 'Composição das câmaras municipais atualizadas.',
                color: 'border-l-yellow-500'
              },
              {
                icon: Building2,
                title: 'Contratos da União',
                desc: 'Licitações e repasses federais via Portal da Transparência.',
                color: 'border-l-red-500'
              },
            ].map(({ icon: Icon, title, desc, color }) => (
              <div key={title} className={`bg-white border border-gray-200 shadow-sm p-6 flex flex-col gap-4 border-l-4 ${color} hover:shadow-md transition-shadow`}>
                <div className="w-12 h-12 bg-gray-100 flex items-center justify-center rounded">
                  <Icon size={24} className="text-gov-dark" />
                </div>
                <div>
                  <h3 className="font-bold text-gov-dark uppercase text-sm tracking-wider mb-2 font-mono">{title}</h3>
                  <p className="text-sm text-gray-600">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
