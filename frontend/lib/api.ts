const API_BASE =
  typeof window !== 'undefined'
    ? (process.env.NEXT_PUBLIC_API_URL || '/gestaobr/api')
    : (process.env.BACKEND_URL || 'http://gestaobr-backend:8000');

export interface Municipio {
  codigo_ibge: string;
  nome: string;
  uf: string;
  populacao: number | null;
  area_km2: number | null;
  densidade: number | null;
}

export interface MunicipioBusca {
  codigo_ibge: string;
  nome: string;
  uf: string;
}

export interface Indicadores {
  codigo_ibge: string;
  pib_per_capita: number | null;
  pib_per_capita_ano: number;
  analfabetismo_pct: number | null;
  esgoto_pct: number | null;
  lixo_pct: number | null;
  fontes: Record<string, string>;
}

export interface Orcamento {
  codigo_ibge: string;
  ano: number;
  disponivel: boolean;
  resumo?: any[];
  receita_total?: number;
  municipio?: string;
  fonte?: string;
}

export interface CamaraInfo {
  codigo_ibge: string;
  n_vereadores: number | null;
  aviso: string;
  fonte: string;
}

export interface Saude {
  disponivel: boolean;
  // Legacy fields
  total_estabelecimentos?: number;
  hospitais?: number;
  ubs?: number;
  // New fields
  total_hospitais?: number;
  total_ubs?: number;
  ubs_centro_saude?: number;
  ubs_postos?: number;
  hospitais_gerais?: number;
  hospitais_especializados?: number;
  upa?: number;
  laboratorios?: number;
  ambulatorios_sus?: number;
}

export interface Educacao {
  disponivel: boolean;
  taxa_escolarizacao?: number;
}

export interface Licitacao {
  numero_controle: string;
  titulo?: string;
  objeto?: string;
  orgao?: string;
  modalidade?: string;
  valor?: number | null;
  ano?: string | number;
  data_abertura?: string;
  data_encerramento?: string;
  data_publicacao?: string;
  url?: string;
}

export interface Licitacoes {
  disponivel: boolean;
  licitacoes?: Licitacao[];
  licitacoes_recentes?: Licitacao[]; // legacy alias
  link_pncp?: string;
  ano?: number;
  total?: number;
  nota?: string;
}

export interface Eleicoes {
  disponivel: boolean;
  eleicao_ano?: number;
  municipio?: string;
  uf?: string;
  tse_resultado_url?: string;
  governanca_municipal?: Record<string, { valor: string; ano: string }>;
  diario_oficial_disponivel?: boolean;
}

export interface Seguranca {
  disponivel: boolean;
  obitos_registrados?: number;
  obitos_ocorridos?: number;
  total_obitos?: number;
  taxa_homicidios_100k?: number; // legacy — not returned anymore
  ano?: string;
  nota?: string;
}

export interface DiarioEdicao {
  data?: string;
  date?: string;
  link?: string;
  url?: string;
  edition_number?: string;
  numero_edicao?: string;
  resumo?: string;
}

export interface DiarioPortal {
  nome: string;
  url: string;
  url_busca?: string;
}

export interface Diario {
  disponivel: boolean;
  total_edicoes?: number;
  total_edicoes_indexadas?: number | null;
  edicoes_recentes?: DiarioEdicao[];
  link_portal?: string;
  link_consulta?: string;
  portal_municipal?: DiarioPortal;
  fonte?: string;
  aviso?: string;
  erro?: string;
}

export interface Emenda {
  autor: string;
  valor: number;
  acao: string;
}

export interface Emendas {
  disponivel: boolean;
  total_emendas?: number;
  valor_total?: number;
  receita_total_realizada?: number;
  receita_per_capita?: number;
  exercicio?: number;
  emendas?: Emenda[];
}

export interface Seguranca {
  disponivel: boolean;
  obitos_registrados?: number;
  obitos_ocorridos?: number;
  total_obitos?: number;
  taxa_homicidios_100k?: number; // legacy — not returned anymore
  ano?: string;
  nota?: string;
}

export interface MeioAmbiente {
  disponivel: boolean;
  bioma?: string;
  area_km2?: number;
}

export async function buscarMunicipios(q: string): Promise<MunicipioBusca[]> {
  const r = await fetch(`${API_BASE}/municipios/busca?q=${encodeURIComponent(q)}`, { next: { revalidate: 86400 } });
  if (!r.ok) return [];
  return r.json();
}

export async function getMunicipio(ibge: string): Promise<Municipio> {
  const r = await fetch(`${API_BASE}/municipios/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) throw new Error('Município não encontrado');
  return r.json();
}

export async function getIndicadores(ibge: string): Promise<Indicadores> {
  const r = await fetch(`${API_BASE}/indicadores/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) throw new Error('Indicadores não disponíveis');
  return r.json();
}

export async function getOrcamento(ibge: string, ano = 2024): Promise<Orcamento> {
  const r = await fetch(`${API_BASE}/orcamento/${ibge}?ano=${ano}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { codigo_ibge: ibge, ano, disponivel: false };
  return r.json();
}

export async function getCamara(ibge: string): Promise<CamaraInfo> {
  const r = await fetch(`${API_BASE}/vereadores/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) throw new Error('Dados não disponíveis');
  return r.json();
}

export async function getContratos(ibge: string, pagina = 1) {
  const r = await fetch(`${API_BASE}/contratos/${ibge}?pagina=${pagina}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { disponivel: false };
  return r.json();
}

export async function getSaude(ibge: string): Promise<Saude> {
  const r = await fetch(`${API_BASE}/saude/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { disponivel: false };
  return r.json();
}

export async function getEducacao(ibge: string): Promise<Educacao> {
  const r = await fetch(`${API_BASE}/educacao/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { disponivel: false };
  return r.json();
}

export async function getLicitacoes(ibge: string): Promise<Licitacoes> {
  const r = await fetch(`${API_BASE}/licitacoes/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { disponivel: false };
  return r.json();
}

export async function getEleicoes(ibge: string): Promise<Eleicoes> {
  const r = await fetch(`${API_BASE}/eleicoes/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { disponivel: false };
  return r.json();
}

export async function getDiario(ibge: string): Promise<Diario> {
  const r = await fetch(`${API_BASE}/diario/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { disponivel: false };
  return r.json();
}

export async function getEmendas(ibge: string): Promise<Emendas> {
  const r = await fetch(`${API_BASE}/emendas/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { disponivel: false };
  return r.json();
}

export async function getSeguranca(ibge: string): Promise<Seguranca> {
  const r = await fetch(`${API_BASE}/seguranca/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { disponivel: false };
  return r.json();
}

export async function getMeioAmbiente(ibge: string): Promise<MeioAmbiente> {
  const r = await fetch(`${API_BASE}/meio_ambiente/${ibge}`, { next: { revalidate: 3600 } });
  if (!r.ok) return { disponivel: false };
  return r.json();
}

// ── New module interfaces ────────────────────────────────────────────────────

export interface Vacinacao {
  ibge: string;
  fonte: string;
  nota?: string;
  link_sipni?: string;
  link_tabnet?: string;
  link_datasus?: string;
  coberturas?: Array<{ vacina: string; cobertura_pct: number; ano: number }>;
}

export interface FndeRepasse {
  programa: string;
  descricao: string;
  valor_referencia?: number;
  link?: string;
}

export interface Fnde {
  ibge: string;
  fonte: string;
  nota?: string;
  link_fnde?: string;
  repasses?: FndeRepasse[];
}

export interface Tcu {
  ibge: string;
  fonte: string;
  nota?: string;
  link_portal?: string;
  link_certidao?: string;
  link_acordaos?: string;
}

export interface FarmaciaPopular {
  ibge: string;
  fonte: string;
  nota?: string;
  link_portal?: string;
  link_credenciadas?: string;
  medicamentos_gratuitos?: string[];
  medicamentos_subsidiados?: string[];
}

export interface Noticia {
  titulo: string;
  link: string;
  data?: string;
  fonte?: string;
  descricao?: string;
}

export interface Noticias {
  ibge: string;
  municipio?: string;
  noticias: Noticia[];
  total?: number;
  fontes?: string[];
}

export interface AnpCombustivel {
  produto: string;
  unidade: string;
}

export interface Anp {
  ibge: string;
  fonte: string;
  nota?: string;
  link_painel?: string;
  link_serie_historica?: string;
  combustiveis?: AnpCombustivel[];
}

export interface Datajud {
  ibge: string;
  fonte: string;
  nota?: string;
  link_consulta?: string;
  link_consulta_publica?: string;
  link_painel_cnj?: string;
  nota_acesso?: string;
}

export interface EmpresaResumo {
  ibge: string;
  fonte: string;
  nota?: string;
  links?: Record<string, string>;
  uso_api?: string;
}

export interface Empresa {
  cnpj?: string;
  razao_social?: string;
  nome_fantasia?: string;
  situacao_cadastral?: string;
  data_abertura?: string;
  porte?: string;
  atividade_principal?: string;
  municipio?: string;
  uf?: string;
}

export interface Ana {
  ibge: string;
  fonte: string;
  nota?: string;
  links?: Record<string, string>;
  datasets_relacionados?: Array<{ titulo: string; descricao: string; link: string }>;
  indicadores_referencia?: Array<{ indicador: string; fonte: string }>;
}

export interface Aneel {
  ibge: string;
  fonte: string;
  nota?: string;
  links?: Record<string, string>;
  tarifas_recentes?: any[];
  indicadores_qualidade?: Array<{ indicador: string; descricao: string }>;
}

// ── New module fetch functions ───────────────────────────────────────────────

export async function getVacinacao(ibge: string): Promise<Vacinacao | null> {
  try {
    const r = await fetch(`${API_BASE}/vacinacao/${ibge}`, { next: { revalidate: 3600 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export async function getFnde(ibge: string): Promise<Fnde | null> {
  try {
    const r = await fetch(`${API_BASE}/fnde/${ibge}`, { next: { revalidate: 3600 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export async function getTcu(ibge: string): Promise<Tcu | null> {
  try {
    const r = await fetch(`${API_BASE}/tcu/${ibge}`, { next: { revalidate: 3600 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export async function getFarmaciaPopular(ibge: string): Promise<FarmaciaPopular | null> {
  try {
    const r = await fetch(`${API_BASE}/farmacia_popular/${ibge}`, { next: { revalidate: 3600 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export async function getNoticias(ibge: string): Promise<Noticias | null> {
  try {
    const r = await fetch(`${API_BASE}/noticias/${ibge}`, { next: { revalidate: 900 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export async function getAnp(ibge: string): Promise<Anp | null> {
  try {
    const r = await fetch(`${API_BASE}/anp/${ibge}`, { next: { revalidate: 3600 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export async function getDatajud(ibge: string): Promise<Datajud | null> {
  try {
    const r = await fetch(`${API_BASE}/datajud/${ibge}`, { next: { revalidate: 86400 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export async function getEmpresasResumo(ibge: string): Promise<EmpresaResumo | null> {
  try {
    const r = await fetch(`${API_BASE}/empresas/${ibge}/resumo`, { next: { revalidate: 3600 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export async function getAna(ibge: string): Promise<Ana | null> {
  try {
    const r = await fetch(`${API_BASE}/ana/${ibge}`, { next: { revalidate: 3600 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export async function getAneel(ibge: string): Promise<Aneel | null> {
  try {
    const r = await fetch(`${API_BASE}/aneel/${ibge}`, { next: { revalidate: 3600 } });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export function formatNum(n: number | null, decimals = 0): string {
  if (n === null || n === undefined) return '—';
  return n.toLocaleString('pt-BR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

export function formatCurrency(n: number | null): string {
  if (n === null || n === undefined) return '—';
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
