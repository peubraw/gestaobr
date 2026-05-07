import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Users, FileText, Building2, TrendingUp, MapPin, AlertCircle, CheckCircle2, Clock, Globe, BarChart3, Gauge, Landmark, Scale, Wallet, Activity, HeartPulse, GraduationCap, ShoppingBag, Vote, Newspaper, Banknote, Shield, Leaf, Bot } from 'lucide-react';
import { getMunicipio, getIndicadores, getOrcamento, getCamara, getContratos, getSaude, getEducacao, getLicitacoes, getEleicoes, getDiario, getEmendas, getSeguranca, getMeioAmbiente, formatNum, Licitacao, Emenda, DiarioEdicao } from '@/lib/api';
import IaGestora from '@/components/IaGestora';

export const dynamic = 'force-dynamic';

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

function GaugeCard({ title, value, pct, invert = false, unit = '%' }: { title: string; value: string; pct: number | null; invert?: boolean; unit?: string }) {
  const isNull = pct === null;
  const safePct = isNull ? 0 : Math.min(100, Math.max(0, pct));
  
  // Invert means lower is better (e.g. analfabetismo)
  const isGood = isNull ? false : invert ? safePct < 30 : safePct > 70;
  const isWarning = isNull ? false : invert ? safePct >= 30 && safePct < 60 : safePct <= 70 && safePct > 40;
  
  const barColor = isNull ? 'bg-gray-200' : isGood ? 'bg-gov-green' : isWarning ? 'bg-gov-yellow' : 'bg-red-600';

  return (
    <div className="bg-gray-50 border border-gov-border p-4 flex flex-col">
      <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 font-mono">{title}</span>
      <div className="flex items-baseline gap-1 mb-3">
        <span className="text-2xl font-bold font-mono text-gov-dark">{isNull ? '—' : value}</span>
        {!isNull && unit && <span className="text-xs font-mono text-gray-500">{unit}</span>}
      </div>
      <div className="w-full h-2 bg-gray-200 mb-1 overflow-hidden">
        <div className={`h-full ${barColor} transition-all duration-1000`} style={{ width: `${safePct}%` }}></div>
      </div>
      <div className="flex justify-between text-[9px] font-mono text-gray-400">
        <span>0{unit}</span>
        <span>100{unit}</span>
      </div>
    </div>
  );
}

function SectionHeader({ icon: Icon, title }: { icon: React.ElementType; title: string }) {
  return (
    <div className="mc-header">
      <Icon size={16} className="text-gov-yellow" />
      {title}
    </div>
  );
}

export default async function MunicipioPage({ params }: { params: Promise<{ ibge: string }> }) {
  const { ibge } = await params;

  let municipio, indicadores, orcamento, camara, contratos;
  let saude, educacao, licitacoes, eleicoes, diario, emendas, seguranca, meioAmbiente;
  try {
    [municipio, indicadores, orcamento, camara, contratos, saude, educacao, licitacoes, eleicoes, diario, emendas, seguranca, meioAmbiente] = await Promise.all([
      getMunicipio(ibge),
      getIndicadores(ibge),
      getOrcamento(ibge),
      getCamara(ibge),
      getContratos(ibge),
      getSaude(ibge),
      getEducacao(ibge),
      getLicitacoes(ibge),
      getEleicoes(ibge),
      getDiario(ibge),
      getEmendas(ibge),
      getSeguranca(ibge),
      getMeioAmbiente(ibge),
    ]);
  } catch {
    notFound();
  }

  // Helper values
  const hasOrçamento = orcamento.disponivel && orcamento.resumo && orcamento.resumo.length > 0;
  const totalReceita = hasOrçamento ? (orcamento.resumo ?? []).find((r: any) => r.no_conta?.toLowerCase().includes('receitas') || r.no_conta?.toLowerCase().includes('total'))?.vl_realizado : null;

  return (
    <div className="flex flex-col gap-6">
      {/* Top Status Bar */}
      <div className="flex flex-wrap items-center justify-between text-xs border-b border-gray-300 pb-2">
        <nav className="flex items-center gap-2 text-gray-500 font-mono">
          <Link href="/gestaobr" className="hover:text-gov-blue flex items-center gap-1">
            <ArrowLeft size={14} /> INÍCIO
          </Link>
          <span>/</span>
          <span className="text-gov-dark font-bold">PAINEL MUNICIPAL</span>
        </nav>
        <div className="flex items-center gap-4 font-mono">
          <span className="flex items-center gap-1 text-gov-green font-bold">
            <span className="w-2 h-2 rounded-full bg-gov-green animate-pulse"></span>
            DADOS SINCRONIZADOS
          </span>
          <span className="text-gray-400 flex items-center gap-1"><Clock size={12} /> REF: 2025</span>
          <div className="hidden md:flex flex-wrap gap-3 text-gov-blue">
            <a href="#indicadores" className="hover:underline">INDICADORES</a>
            <a href="#financas" className="hover:underline">FINANÇAS</a>
            <a href="#legislativo" className="hover:underline">LEGISLATIVO</a>
            <a href="#contratos" className="hover:underline">CONTRATOS</a>
            <a href="#saude" className="hover:underline">SAÚDE</a>
            <a href="#educacao" className="hover:underline">EDUCAÇÃO</a>
            <a href="#licitacoes" className="hover:underline">LICITAÇÕES</a>
            <a href="#eleicoes" className="hover:underline">ELEIÇÕES</a>
            <a href="#diario" className="hover:underline">DIÁRIO</a>
            <a href="#emendas" className="hover:underline">EMENDAS</a>
            <a href="#seguranca" className="hover:underline">SEGURANÇA</a>
            <a href="#meioambiente" className="hover:underline">MEIO AMBIENTE</a>
            <a href="#ia-gestora" className="hover:underline flex items-center gap-1"><Bot size={12} /> IA GESTORA</a>
          </div>
        </div>
      </div>

      {/* Header do município - Mission Control Style */}
      <section className="bg-gray-100 border border-gov-border p-4 shadow-inner">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6 mb-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-4xl font-black text-gov-dark uppercase tracking-tight">{municipio.nome}</h1>
              <span className="bg-gov-dark text-white font-mono font-bold px-3 py-1 text-lg">{municipio.uf}</span>
            </div>
            <p className="text-gov-blue font-mono font-bold flex items-center gap-2">
              <Globe size={14} /> CÓDIGO IBGE: {ibge}
            </p>
          </div>
        </div>

        {/* 5 KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <KpiCard title="População" value={formatNum(municipio.populacao)} unit="hab" icon={Users} />
          <KpiCard title="Área Total" value={formatNum(municipio.area_km2, 0)} unit="km²" icon={MapPin} />
          <KpiCard title="Densidade" value={municipio.densidade ? formatNum(municipio.densidade, 1) : '—'} unit="hab/km²" icon={Activity} />
          <KpiCard title="PIB Per Capita" value={indicadores.pib_per_capita ? formatNum(indicadores.pib_per_capita, 0) : '—'} unit="R$" icon={Wallet} />
          <KpiCard title="Vereadores" value={camara.n_vereadores?.toString() || '—'} unit="assentos" icon={Scale} />
        </div>
      </section>

      {/* Grid 12 colunas */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Coluna Esquerda (7) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          
          {/* Indicadores Vitais */}
          <section id="indicadores" className="mc-card">
            <SectionHeader icon={Gauge} title="Indicadores Vitais" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <GaugeCard 
                title="Analfabetismo (15+ anos)" 
                value={indicadores.analfabetismo_pct ? formatNum(indicadores.analfabetismo_pct, 1) : '—'} 
                pct={indicadores.analfabetismo_pct} 
                invert={true} 
              />
              <GaugeCard 
                title="Cobertura de Esgoto" 
                value={indicadores.esgoto_pct ? formatNum(indicadores.esgoto_pct, 1) : '—'} 
                pct={indicadores.esgoto_pct} 
              />
              <GaugeCard 
                title="Coleta de Lixo" 
                value={indicadores.lixo_pct ? formatNum(indicadores.lixo_pct, 1) : '—'} 
                pct={indicadores.lixo_pct} 
              />
              <div className="bg-gray-50 border border-gov-border p-4 flex flex-col justify-center">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 font-mono">PIB MUNICIPAL</span>
                <span className="text-2xl font-bold font-mono text-gov-dark mb-2">
                  {indicadores.pib_per_capita ? `R$ ${formatNum(indicadores.pib_per_capita, 0)}` : '—'}
                  <span className="text-xs font-mono text-gray-500 ml-1">/ cap</span>
                </span>
                <div className="text-[10px] text-gray-400 font-mono mt-auto flex items-center gap-1">
                  <CheckCircle2 size={10} className="text-gov-green" /> FONTE: IBGE {indicadores.pib_per_capita_ano}
                </div>
              </div>
            </div>
          </section>

          {/* Orçamento Municipal */}
          <section id="financas" className="mc-card">
            <SectionHeader icon={Landmark} title={`Execução Orçamentária (${orcamento.ano})`} />
            
            {hasOrçamento ? (
              <div className="flex flex-col gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gov-dark text-white p-4">
                    <div className="text-[10px] font-mono text-gray-400 mb-1">RECEITA TOTAL REPORTADA</div>
                    <div className="text-2xl font-mono font-bold text-gov-green">
                      R$ {totalReceita ? Number(totalReceita).toLocaleString('pt-BR') : '—'}
                    </div>
                  </div>
                  <div className="bg-gray-100 p-4 border border-gov-border">
                    <div className="text-[10px] font-mono text-gray-500 mb-1">SITUAÇÃO DOS DADOS</div>
                    <div className="text-sm font-bold text-gov-dark flex items-center gap-2">
                      <CheckCircle2 size={16} className="text-gov-green" /> REGISTRADO (SICONFI)
                    </div>
                  </div>
                </div>
                
                <div className="overflow-x-auto mt-2">
                  <table className="w-full text-left border-collapse font-mono text-xs">
                    <thead>
                      <tr className="bg-gray-200 text-gov-dark">
                        <th className="p-2 border border-gray-300">CONTA</th>
                        <th className="p-2 border border-gray-300 text-right">PREVISTO (R$)</th>
                        <th className="p-2 border border-gray-300 text-right">REALIZADO (R$)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(orcamento.resumo ?? []).slice(0, 8).map((row: any, i: number) => (
                        <tr key={i} className="hover:bg-blue-50">
                          <td className="p-2 border border-gray-200 truncate max-w-[200px]">{row.no_conta || row.ds_conta || '—'}</td>
                          <td className="p-2 border border-gray-200 text-right">{row.vl_orcado_atualizado ? Number(row.vl_orcado_atualizado).toLocaleString('pt-BR') : '—'}</td>
                          <td className="p-2 border border-gray-200 text-right font-bold text-gov-dark">{row.vl_realizado ? Number(row.vl_realizado).toLocaleString('pt-BR') : '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600">
                <AlertCircle size={20} className="text-red-500" />
                <span>DADOS ORÇAMENTÁRIOS NÃO CONSOLIDADOS NO SICONFI.</span>
              </div>
            )}
          </section>

          {/* Saúde */}
          <section id="saude" className="mc-card">
            <SectionHeader icon={HeartPulse} title="Saúde Pública" />
            {saude.disponivel ? (
              <div className="grid grid-cols-2 gap-3">
                <KpiCard title="Total Estabelecimentos" value={saude.total_estabelecimentos?.toString() || '—'} icon={HeartPulse} />
                <KpiCard title="Hospitais" value={saude.hospitais?.toString() || '—'} icon={Building2} />
                <KpiCard title="UBS" value={saude.ubs?.toString() || '—'} icon={Activity} />
                <KpiCard title="Laboratórios" value={saude.laboratorios?.toString() || '—'} icon={FileText} />
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600">
                <AlertCircle size={20} className="text-gray-400" />
                <span>DADOS DE SAÚDE NÃO DISPONÍVEIS.</span>
              </div>
            )}
          </section>

          {/* Educação */}
          <section id="educacao" className="mc-card">
            <SectionHeader icon={GraduationCap} title="Educação" />
            {educacao.disponivel ? (
              <div className="grid grid-cols-1 gap-4">
                <GaugeCard 
                  title="Taxa de Escolarização (6 a 14 anos)" 
                  value={educacao.taxa_escolarizacao ? formatNum(educacao.taxa_escolarizacao, 1) : '—'} 
                  pct={educacao.taxa_escolarizacao ?? null} 
                />
                <div className="text-[9px] font-mono text-gray-400 text-right uppercase">
                  FONTE: IBGE / INEP
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600">
                <AlertCircle size={20} className="text-gray-400" />
                <span>DADOS DE EDUCAÇÃO NÃO DISPONÍVEIS.</span>
              </div>
            )}
          </section>

          {/* Licitações */}
          <section id="licitacoes" className="mc-card">
            <SectionHeader icon={ShoppingBag} title="Licitações Recentes" />
            {licitacoes.disponivel && licitacoes.licitacoes && licitacoes.licitacoes.length > 0 ? (
              <div className="flex flex-col gap-2">
                {licitacoes.licitacoes.map((lic: Licitacao, i: number) => (
                  <div key={i} className="flex flex-col p-3 bg-gray-50 border border-gray-200 hover:border-gov-blue transition-colors">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs font-mono font-bold text-gov-dark">{lic.numero || 'S/N'}</span>
                      <span className="text-[10px] font-mono text-gov-green font-bold">
                        R$ {lic.valor ? Number(lic.valor).toLocaleString('pt-BR') : '—'}
                      </span>
                    </div>
                    <div className="text-[10px] text-gray-500 line-clamp-2 italic mb-2">
                      {lic.objeto || '—'}
                    </div>
                    <div className="text-[9px] font-mono font-bold uppercase text-gov-blue">
                      SITUAÇÃO: {lic.situacao || '—'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600">
                <AlertCircle size={20} className="text-gray-400" />
                <span>NENHUMA LICITAÇÃO RECENTE ENCONTRADA.</span>
              </div>
            )}
          </section>

          {/* Emendas */}
          <section id="emendas" className="mc-card">
            <SectionHeader icon={Banknote} title="Emendas Parlamentares" />
            {emendas.disponivel ? (
              <div className="flex flex-col gap-4">
                <div className="grid grid-cols-2 gap-3">
                  <KpiCard title="Total de Emendas" value={emendas.total_emendas?.toString() || '—'} icon={FileText} />
                  <KpiCard title="Valor Total" value={emendas.valor_total ? formatNum(emendas.valor_total, 0) : '—'} unit="R$" icon={Wallet} />
                </div>
                {emendas.emendas && emendas.emendas.length > 0 && (
                  <div className="overflow-x-auto mt-2">
                    <table className="w-full text-left border-collapse font-mono text-xs">
                      <thead>
                        <tr className="bg-gray-200 text-gov-dark">
                          <th className="p-2 border border-gray-300">AUTOR</th>
                          <th className="p-2 border border-gray-300">AÇÃO</th>
                          <th className="p-2 border border-gray-300 text-right">VALOR (R$)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {emendas.emendas.map((em: Emenda, i: number) => (
                          <tr key={i} className="hover:bg-blue-50">
                            <td className="p-2 border border-gray-200 truncate max-w-[120px] font-bold">{em.autor || '—'}</td>
                            <td className="p-2 border border-gray-200 truncate max-w-[150px]">{em.acao || '—'}</td>
                            <td className="p-2 border border-gray-200 text-right font-bold text-gov-dark">{em.valor ? Number(em.valor).toLocaleString('pt-BR') : '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600">
                <AlertCircle size={20} className="text-gray-400" />
                <span>DADOS DE EMENDAS NÃO DISPONÍVEIS.</span>
              </div>
            )}
          </section>

        </div>

        {/* Coluna Direita (5) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          
          {/* Câmara Municipal */}
          <section id="legislativo" className="mc-card">
            <SectionHeader icon={Scale} title="Poder Legislativo" />
            {camara.n_vereadores ? (
              <div className="flex flex-col items-center">
                <div className="text-[10px] font-mono text-gray-500 mb-2 w-full">COMPOSIÇÃO DA CÂMARA (ASSENTOS)</div>
                <div className="text-5xl font-black text-gov-blue font-mono mb-4">{camara.n_vereadores}</div>
                
                {/* Visual dots representation */}
                <div className="flex flex-wrap justify-center gap-1.5 p-4 bg-gray-50 border border-gov-border w-full">
                  {Array.from({ length: camara.n_vereadores }).map((_, i) => (
                    <div key={i} className="w-3 h-3 rounded-full bg-gov-blue" title={`Assento ${i+1}`}></div>
                  ))}
                </div>
                <div className="text-[9px] font-mono text-gray-400 mt-3 w-full text-right uppercase">
                  FONTE: {camara.fonte || 'IBGE MUNIC'}
                </div>
              </div>
            ) : (
               <div className="flex items-center gap-3 bg-yellow-50 border border-yellow-200 p-4 text-sm font-mono text-yellow-800">
                <AlertCircle size={20} className="text-yellow-600" />
                <span>{camara.aviso || 'Dados não disponíveis'}</span>
              </div>
            )}
          </section>

          {/* Contratos Federais */}
          <section id="contratos" className="mc-card flex-1">
            <SectionHeader icon={Building2} title="Contratos da União" />
            {contratos.disponivel && contratos.dados && Array.isArray(contratos.dados) && contratos.dados.length > 0 ? (
              <div className="flex flex-col gap-2">
                <div className="text-[10px] font-mono text-gray-500 mb-1">REGISTROS RECENTES (PORTAL DA TRANSPARÊNCIA)</div>
                {contratos.dados.slice(0, 6).map((c: any, i: number) => (
                  <div key={i} className="flex flex-col p-2 bg-gray-50 border border-gray-200 hover:border-gov-blue transition-colors">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs font-mono font-bold text-gov-dark">{c.numero || 'S/N'}</span>
                      <span className="text-[10px] font-mono text-gov-green font-bold">
                        R$ {c.valorInicialCompra ? Number(c.valorInicialCompra).toLocaleString('pt-BR') : '—'}
                      </span>
                    </div>
                    <div className="text-[10px] font-mono text-gray-600 truncate uppercase">
                      {c.fornecedor?.nome || c.nomeFornecedor || 'FORNECEDOR NÃO IDENTIFICADO'}
                    </div>
                    <div className="text-[10px] text-gray-500 line-clamp-1 italic">
                      {c.objeto || c.objetoContrato || '—'}
                    </div>
                  </div>
                ))}
                <a href={`https://www.portaltransparencia.gov.br/municipios/${ibge}`} target="_blank" rel="noreferrer" className="mt-2 text-center text-[10px] font-mono font-bold text-gov-blue hover:underline uppercase bg-blue-50 py-2">
                  VER TODOS NO PORTAL DA TRANSPARÊNCIA →
                </a>
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600 mt-auto mb-auto">
                <AlertCircle size={20} className="text-gray-400" />
                <span>NENHUM REGISTRO DE CONTRATO FEDERAL LOCALIZADO.</span>
              </div>
            )}
          </section>

          {/* Segurança */}
          <section id="seguranca" className="mc-card">
            <SectionHeader icon={Shield} title="Segurança Pública" />
            {seguranca.disponivel ? (
              <div className="flex flex-col gap-4">
                <GaugeCard 
                  title={`Taxa de Homicídios (${seguranca.ano || '2023'})`} 
                  value={seguranca.taxa_homicidios_100k ? formatNum(seguranca.taxa_homicidios_100k, 1) : '—'} 
                  pct={seguranca.taxa_homicidios_100k ?? null} 
                  invert={true}
                  unit="/100k"
                />
                <div className="text-[9px] font-mono text-gray-400 text-right uppercase">
                  FONTE: IBGE / DATASUS
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600">
                <AlertCircle size={20} className="text-gray-400" />
                <span>DADOS DE SEGURANÇA NÃO DISPONÍVEIS.</span>
              </div>
            )}
          </section>

          {/* Meio Ambiente */}
          <section id="meioambiente" className="mc-card">
            <SectionHeader icon={Leaf} title="Meio Ambiente" />
            {meioAmbiente.disponivel ? (
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 border border-gov-border p-3 flex flex-col justify-center">
                  <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 font-mono">Bioma Predominante</span>
                  <div className="inline-flex items-center justify-center px-3 py-1 bg-gov-green text-white font-bold text-sm uppercase rounded w-full">
                    {meioAmbiente.bioma || '—'}
                  </div>
                </div>
                <KpiCard title="Área Preservada" value={meioAmbiente.area_km2 ? formatNum(meioAmbiente.area_km2, 1) : '—'} unit="km²" icon={MapPin} />
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600">
                <AlertCircle size={20} className="text-gray-400" />
                <span>DADOS DE MEIO AMBIENTE NÃO DISPONÍVEIS.</span>
              </div>
            )}
          </section>

          {/* Eleições */}
          <section id="eleicoes" className="mc-card">
            <SectionHeader icon={Vote} title={`Eleições (${eleicoes.eleicao_ano || 'Recentes'})`} />
            {eleicoes.disponivel ? (
              <div className="flex flex-col gap-2">
                <div className="bg-gov-blue text-white p-4 flex flex-col items-center justify-center text-center">
                  <Vote size={32} className="mb-2 opacity-80" />
                  <span className="text-lg font-bold uppercase tracking-wider font-mono">Resultados Eleitorais</span>
                  <a href={`https://resultados.tse.jus.br/`} target="_blank" rel="noreferrer" className="mt-3 text-xs font-bold underline hover:text-gov-yellow">
                    CONSULTAR NO PORTAL DO TSE
                  </a>
                </div>
                <div className="text-[9px] font-mono text-gray-400 text-right uppercase">
                  FONTE: TRIBUNAL SUPERIOR ELEITORAL
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600">
                <AlertCircle size={20} className="text-gray-400" />
                <span>DADOS ELEITORAIS NÃO DISPONÍVEIS.</span>
              </div>
            )}
          </section>

          {/* Diário Oficial */}
          <section id="diario" className="mc-card">
            <SectionHeader icon={Newspaper} title="Diário Oficial do Município" />
            {diario.disponivel ? (
              <div className="flex flex-col gap-3">
                <div className="bg-gray-50 border border-gov-border p-3 flex justify-between items-center">
                  <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest font-mono">Edições Indexadas</span>
                  <span className="text-xl font-bold text-gov-dark font-mono">{diario.total_edicoes || 0}</span>
                </div>
                {diario.edicoes_recentes && diario.edicoes_recentes.length > 0 && (
                  <div className="flex flex-col gap-2">
                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest font-mono">Últimas Publicações</span>
                    {diario.edicoes_recentes.slice(0, 3).map((ed: DiarioEdicao, i: number) => (
                      <a key={i} href={ed.link} target="_blank" rel="noreferrer" className="flex items-center justify-between p-2 border border-gray-200 hover:border-gov-blue hover:bg-blue-50 transition-colors">
                        <span className="text-xs font-mono font-bold text-gov-dark">{ed.data}</span>
                        <span className="text-[10px] font-bold text-gov-blue uppercase">Visualizar →</span>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-3 bg-gray-100 border border-gray-300 p-4 text-sm font-mono text-gray-600">
                <AlertCircle size={20} className="text-gray-400" />
                <span>DIÁRIO OFICIAL NÃO INDEXADO.</span>
              </div>
            )}
          </section>

        </div>
      </div>

      {/* IA Gestora Section */}
      <section id="ia-gestora" className="mc-card">
        <SectionHeader icon={Bot} title="IA Gestora Municipal" />
        <IaGestora ibge={ibge} nomeMunicipio={municipio.nome} />
      </section>
    </div>
  );
}
