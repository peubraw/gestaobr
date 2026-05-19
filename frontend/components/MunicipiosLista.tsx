'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Search, ChevronRight, MapPin } from 'lucide-react';
import { EstadoMunicipio } from '@/lib/api';

export default function MunicipiosLista({ municipios, uf }: { municipios: EstadoMunicipio[]; uf: string }) {
  const [query, setQuery] = useState('');

  const filtered = query.length >= 2
    ? municipios.filter(m => m.nome.toLowerCase().includes(query.toLowerCase()))
    : municipios;

  return (
    <div>
      {/* Search */}
      <div className="flex items-center bg-white border-2 border-gov-border mb-4 shadow-sm">
        <Search size={16} className="ml-3 text-gray-400 flex-shrink-0" />
        <input
          type="text"
          placeholder={`FILTRAR ENTRE ${municipios.length} MUNICÍPIOS...`}
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="flex-1 px-3 py-2.5 text-sm font-mono text-gov-dark placeholder:text-gray-400 uppercase outline-none bg-transparent"
          autoComplete="off"
        />
        {query && (
          <button
            onClick={() => setQuery('')}
            className="mr-3 text-xs font-mono text-gray-400 hover:text-gov-dark"
          >
            ✕
          </button>
        )}
      </div>

      {/* Count badge */}
      <div className="text-xs font-mono text-gray-500 mb-3">
        EXIBINDO {filtered.length} DE {municipios.length} MUNICÍPIOS
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
        {filtered.map(m => (
          <Link
            key={m.codigo_ibge}
            href={`/municipio/${m.codigo_ibge}`}
            className="flex items-center gap-2 bg-white border border-gov-border hover:border-gov-blue hover:bg-blue-50 p-3 transition-colors group"
          >
            <MapPin size={14} className="text-gov-blue flex-shrink-0 group-hover:text-gov-yellow" />
            <span className="flex-1 text-sm font-mono font-bold text-gov-dark group-hover:text-gov-blue uppercase truncate">
              {m.nome}
            </span>
            <ChevronRight size={14} className="text-gray-300 group-hover:text-gov-blue flex-shrink-0" />
          </Link>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center text-sm font-mono text-gray-400 py-8 border border-dashed border-gray-200">
          NENHUM MUNICÍPIO ENCONTRADO PARA &quot;{query.toUpperCase()}&quot;
        </div>
      )}
    </div>
  );
}
