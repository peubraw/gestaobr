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
  fonte?: string;
}

export interface CamaraInfo {
  codigo_ibge: string;
  n_vereadores: number | null;
  aviso: string;
  fonte: string;
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

export async function getOrcamento(ibge: string, ano = 2023): Promise<Orcamento> {
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

export function formatNum(n: number | null, decimals = 0): string {
  if (n === null || n === undefined) return '—';
  return n.toLocaleString('pt-BR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

export function formatCurrency(n: number | null): string {
  if (n === null || n === undefined) return '—';
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
