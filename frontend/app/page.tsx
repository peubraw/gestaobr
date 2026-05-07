'use client';

import { useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Search, MapPin, ChevronRight, Building2, Users, FileText, TrendingUp } from 'lucide-react';
import { MunicipioBusca } from '@/lib/api';

async function buscarMunicipiosClient(q: string): Promise<MunicipioBusca[]> {
  const base = process.env.NEXT_PUBLIC_API_URL || '/gestaobr/api';
  const r = await fetch(`${base}/municipios/busca?q=${encodeURIComponent(q)}`);
  if (!r.ok) return [];
  return r.json();
}

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
    <div className="flex flex-col gap-12">
      {/* Hero */}
      <section className="text-center py-12">
        <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-200 text-gov-blue text-sm font-medium px-4 py-1.5 rounded-full mb-6">
          <span className="w-2 h-2 rounded-full bg-gov-blue animate-pulse"></span>
          Dados atualizados com fontes oficiais
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-gov-dark mb-4 leading-tight">
          Painel de Gestão<br />
          <span className="text-gov-blue">Municipal</span>
        </h1>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-10">
          Acesse dados públicos consolidados sobre orçamento, indicadores sociais,
          câmara de vereadores e contratos do seu município.
        </p>

        {/* Search box */}
        <div className="relative max-w-xl mx-auto">
          <div className="flex items-center bg-white border-2 border-gov-blue rounded-lg shadow-lg overflow-visible">
            <Search size={20} className="ml-4 text-gov-blue flex-shrink-0" />
            <input
              type="text"
              placeholder="Digite o nome do município..."
              value={query}
              onChange={e => handleInput(e.target.value)}
              className="flex-1 px-4 py-4 text-base outline-none bg-transparent"
              autoComplete="off"
            />
            {loading && (
              <div className="mr-4 w-5 h-5 border-2 border-gov-blue border-t-transparent rounded-full animate-spin" />
            )}
          </div>

          {/* Dropdown resultados */}
          {results.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gov-border rounded-lg shadow-xl z-50 max-h-72 overflow-y-auto">
              {results.map(m => (
                <button
                  key={m.codigo_ibge}
                  onClick={() => handleSelect(m)}
                  className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-blue-50 transition-colors border-b border-gray-100 last:border-0"
                >
                  <MapPin size={16} className="text-gov-blue flex-shrink-0" />
                  <span className="flex-1 font-medium text-gov-text">{m.nome}</span>
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-mono">{m.uf}</span>
                  <ChevronRight size={14} className="text-gray-400" />
                </button>
              ))}
            </div>
          )}

          {query.length >= 2 && !loading && results.length === 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gov-border rounded-lg shadow-xl z-50 px-4 py-3 text-sm text-gray-500">
              Nenhum município encontrado para &ldquo;{query}&rdquo;
            </div>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          {
            icon: TrendingUp,
            title: 'Indicadores Socioeconômicos',
            desc: 'PIB per capita, IDHM, analfabetismo, saneamento e coleta de lixo via IBGE.',
          },
          {
            icon: FileText,
            title: 'Orçamento Municipal',
            desc: 'Receitas e despesas da LOA executada via SICONFI (Tesouro Nacional).',
          },
          {
            icon: Users,
            title: 'Câmara de Vereadores',
            desc: 'Composição da câmara municipal com dados do IBGE Munic.',
          },
          {
            icon: Building2,
            title: 'Contratos e Obras',
            desc: 'Contratos e licitações federais no município via Portal da Transparência.',
          },
        ].map(({ icon: Icon, title, desc }) => (
          <div key={title} className="card flex flex-col gap-3">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <Icon size={20} className="text-gov-blue" />
            </div>
            <h3 className="font-bold text-gov-dark">{title}</h3>
            <p className="text-sm text-gray-600 leading-relaxed">{desc}</p>
          </div>
        ))}
      </section>

      {/* Fontes */}
      <section className="card">
        <h2 className="section-title">Fontes de Dados</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {[
            { nome: 'IBGE', desc: 'Censo, Sidra, Munic' },
            { nome: 'STN/SICONFI', desc: 'Orçamento e finanças' },
            { nome: 'CGU', desc: 'Portal da Transparência' },
            { nome: 'BrasilAPI', desc: 'Dados municipais' },
          ].map(f => (
            <div key={f.nome} className="flex flex-col gap-1 p-3 bg-gray-50 rounded border border-gov-border">
              <span className="font-bold text-gov-blue">{f.nome}</span>
              <span className="text-gray-500 text-xs">{f.desc}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
