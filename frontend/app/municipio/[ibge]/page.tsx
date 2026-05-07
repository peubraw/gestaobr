import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Users, FileText, Building2, TrendingUp, MapPin, AlertCircle, CheckCircle } from 'lucide-react';
import { getMunicipio, getIndicadores, getOrcamento, getCamara, getContratos, formatNum } from '@/lib/api';

export const dynamic = 'force-dynamic';

function StatCard({ label, value, unit, source }: { label: string; value: string; unit?: string; source?: string }) {
  return (
    <div className="card flex flex-col gap-1">
      <span className="text-xs text-gray-500 font-semibold uppercase tracking-wider">{label}</span>
      <div className="flex items-end gap-1">
        <span className="text-2xl font-bold text-gov-dark">{value}</span>
        {unit && <span className="text-sm text-gray-500 mb-0.5">{unit}</span>}
      </div>
      {source && <span className="text-xs text-gray-400 mt-1">{source}</span>}
    </div>
  );
}

function SectionHeader({ icon: Icon, title }: { icon: React.ElementType; title: string }) {
  return (
    <div className="flex items-center gap-3 mb-5 border-l-4 border-gov-blue pl-3">
      <Icon size={20} className="text-gov-blue" />
      <h2 className="text-xl font-bold text-gov-dark">{title}</h2>
    </div>
  );
}

function DataRow({ label, value, unit }: { label: string; value: string; unit?: string }) {
  return (
    <tr>
      <td className="px-4 py-2.5 border-b border-gov-border text-gray-600 font-medium w-1/2">{label}</td>
      <td className="px-4 py-2.5 border-b border-gov-border text-gov-dark font-semibold">
        {value}{unit ? <span className="text-gray-500 font-normal text-sm ml-1">{unit}</span> : null}
      </td>
    </tr>
  );
}

export default async function MunicipioPage({ params }: { params: Promise<{ ibge: string }> }) {
  const { ibge } = await params;

  let municipio, indicadores, orcamento, camara, contratos;
  try {
    [municipio, indicadores, orcamento, camara, contratos] = await Promise.all([
      getMunicipio(ibge),
      getIndicadores(ibge),
      getOrcamento(ibge),
      getCamara(ibge),
      getContratos(ibge),
    ]);
  } catch {
    notFound();
  }

  return (
    <div className="flex flex-col gap-8 pb-16">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-gray-500">
        <Link href="/gestaobr" className="hover:text-gov-blue flex items-center gap-1">
          <ArrowLeft size={14} /> Início
        </Link>
        <span>/</span>
        <span className="text-gov-dark font-medium">{municipio.nome} — {municipio.uf}</span>
      </nav>

      {/* Header do município */}
      <section className="card">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <MapPin size={20} className="text-gov-blue" />
              <h1 className="text-3xl font-bold text-gov-dark">{municipio.nome}</h1>
              <span className="bg-gov-blue text-white text-sm font-bold px-2.5 py-0.5 rounded">{municipio.uf}</span>
            </div>
            <p className="text-gray-500 text-sm">Código IBGE: <span className="font-mono font-semibold text-gray-700">{ibge}</span></p>
          </div>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
            <div className="bg-blue-50 border border-blue-100 rounded p-3 text-center">
              <div className="text-xl font-bold text-gov-blue">{formatNum(municipio.populacao)}</div>
              <div className="text-xs text-gray-500">habitantes (2021)</div>
            </div>
            <div className="bg-blue-50 border border-blue-100 rounded p-3 text-center">
              <div className="text-xl font-bold text-gov-blue">{formatNum(municipio.area_km2, 0)}</div>
              <div className="text-xs text-gray-500">km² de área</div>
            </div>
            <div className="bg-blue-50 border border-blue-100 rounded p-3 text-center">
              <div className="text-xl font-bold text-gov-blue">{municipio.densidade ? formatNum(municipio.densidade, 1) : '—'}</div>
              <div className="text-xs text-gray-500">hab./km²</div>
            </div>
          </div>
        </div>
      </section>

      {/* Indicadores socioeconômicos */}
      <section className="card">
        <SectionHeader icon={TrendingUp} title="Indicadores Socioeconômicos" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <StatCard
            label="PIB per capita"
            value={indicadores.pib_per_capita ? `R$ ${formatNum(indicadores.pib_per_capita, 0)}` : '—'}
            source={`IBGE ${indicadores.pib_per_capita_ano}`}
          />
          <StatCard
            label="Analfabetismo 15+"
            value={indicadores.analfabetismo_pct ? `${formatNum(indicadores.analfabetismo_pct, 1)}%` : '—'}
            source="Censo 2022"
          />
          <StatCard
            label="Rede de Esgoto"
            value={indicadores.esgoto_pct ? `${formatNum(indicadores.esgoto_pct, 1)}%` : '—'}
            source="Censo 2022"
          />
          <StatCard
            label="Coleta de Lixo"
            value={indicadores.lixo_pct ? `${formatNum(indicadores.lixo_pct, 1)}%` : '—'}
            source="Censo 2022"
          />
        </div>
        <div className="text-xs text-gray-400 flex items-center gap-1 mt-2">
          <CheckCircle size={12} className="text-gov-green" />
          Fonte: IBGE Sidra — Censo 2022 e PIB Municipal
        </div>
      </section>

      {/* Câmara municipal */}
      <section className="card">
        <SectionHeader icon={Users} title="Câmara de Vereadores" />
        {camara.n_vereadores ? (
          <div className="flex items-center gap-6">
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-6 text-center">
              <div className="text-4xl font-bold text-gov-blue">{camara.n_vereadores}</div>
              <div className="text-sm text-gray-500 mt-1">vereadores</div>
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-600 mb-2">
                A câmara municipal de <strong>{municipio.nome}</strong> é composta por{' '}
                <strong>{camara.n_vereadores} vereadores</strong> conforme o IBGE Munic 2023.
              </p>
              <p className="text-xs text-gray-400">{camara.fonte}</p>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-3 bg-yellow-50 border border-yellow-200 rounded p-4">
            <AlertCircle size={18} className="text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-yellow-800">Dados individuais não disponíveis via API nacional</p>
              <p className="text-xs text-yellow-700 mt-1">{camara.aviso}</p>
            </div>
          </div>
        )}
      </section>

      {/* Orçamento */}
      <section className="card">
        <SectionHeader icon={FileText} title={`Orçamento ${orcamento.ano}`} />
        {orcamento.disponivel && orcamento.resumo && orcamento.resumo.length > 0 ? (
          <div>
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Conta</th>
                    <th>Valor Previsto (R$)</th>
                    <th>Valor Realizado (R$)</th>
                  </tr>
                </thead>
                <tbody>
                  {orcamento.resumo.slice(0, 15).map((row: any, i: number) => (
                    <tr key={i}>
                      <td>{row.no_conta || row.ds_conta || '—'}</td>
                      <td className="font-mono">{row.vl_orcado_atualizado ? Number(row.vl_orcado_atualizado).toLocaleString('pt-BR') : '—'}</td>
                      <td className="font-mono">{row.vl_realizado ? Number(row.vl_realizado).toLocaleString('pt-BR') : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-gray-400 mt-3">Fonte: {orcamento.fonte}</p>
          </div>
        ) : (
          <div className="flex items-start gap-3 bg-gray-50 border border-gov-border rounded p-4">
            <AlertCircle size={18} className="text-gray-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-700">Dados orçamentários não disponíveis</p>
              <p className="text-xs text-gray-500 mt-1">
                Os dados do SICONFI podem não estar disponíveis para este município.
                Consulte diretamente o{' '}
                <a href="https://siconfi.tesouro.gov.br" target="_blank" rel="noreferrer" className="text-gov-blue underline">
                  portal SICONFI
                </a>.
              </p>
            </div>
          </div>
        )}
      </section>

      {/* Contratos */}
      <section className="card">
        <SectionHeader icon={Building2} title="Contratos Federais" />
        {contratos.disponivel && contratos.dados && Array.isArray(contratos.dados) && contratos.dados.length > 0 ? (
          <div>
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Nº Contrato</th>
                    <th>Fornecedor</th>
                    <th>Objeto</th>
                    <th>Valor (R$)</th>
                    <th>Vigência</th>
                  </tr>
                </thead>
                <tbody>
                  {contratos.dados.slice(0, 10).map((c: any, i: number) => (
                    <tr key={i}>
                      <td className="font-mono text-xs">{c.numero || '—'}</td>
                      <td>{c.fornecedor?.nome || c.nomeFornecedor || '—'}</td>
                      <td className="max-w-xs truncate">{c.objeto || c.objetoContrato || '—'}</td>
                      <td className="font-mono">{c.valorInicialCompra ? Number(c.valorInicialCompra).toLocaleString('pt-BR') : '—'}</td>
                      <td className="text-xs">{c.dataInicioVigencia ? c.dataInicioVigencia.slice(0, 10) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-gray-400 mt-3">Fonte: Portal da Transparência — CGU</p>
          </div>
        ) : (
          <div className="flex items-start gap-3 bg-gray-50 border border-gov-border rounded p-4">
            <AlertCircle size={18} className="text-gray-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-700">Nenhum contrato federal encontrado</p>
              <p className="text-xs text-gray-500 mt-1">
                Consulte diretamente o{' '}
                <a href={`https://www.portaltransparencia.gov.br/municipios/${ibge}`} target="_blank" rel="noreferrer" className="text-gov-blue underline">
                  Portal da Transparência
                </a>.
              </p>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
