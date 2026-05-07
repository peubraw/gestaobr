export default function SobrePage() {
  return (
    <div className="max-w-3xl flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold text-gov-dark mb-2">Sobre o GestãoBR</h1>
        <p className="text-gray-600">
          Painel de dados públicos consolidados para gestores municipais — prefeitos, vereadores e equipes técnicas.
        </p>
      </div>

      <section className="card">
        <h2 className="section-title">Objetivo</h2>
        <p className="text-gray-700 leading-relaxed">
          O GestãoBR foi desenvolvido para facilitar o acesso a dados públicos já existentes,
          reunindo em um único painel informações de diversas fontes oficiais do governo federal.
          A ferramenta é especialmente útil para gestores que assumem novos mandatos e precisam
          de um diagnóstico rápido da situação do município.
        </p>
      </section>

      <section className="card">
        <h2 className="section-title">Fontes de Dados</h2>
        <div className="flex flex-col gap-4 text-sm">
          {[
            {
              nome: 'IBGE — Instituto Brasileiro de Geografia e Estatística',
              url: 'https://ibge.gov.br',
              dados: 'População, PIB per capita, indicadores de saneamento, educação (Censo 2022), Munic.',
            },
            {
              nome: 'STN — Secretaria do Tesouro Nacional (SICONFI)',
              url: 'https://siconfi.tesouro.gov.br',
              dados: 'Execução orçamentária, receitas e despesas municipais (LOA).',
            },
            {
              nome: 'CGU — Portal da Transparência',
              url: 'https://portaldatransparencia.gov.br',
              dados: 'Contratos federais, licitações e transferências no município.',
            },
            {
              nome: 'BrasilAPI',
              url: 'https://brasilapi.com.br',
              dados: 'Lista de municípios por UF e código IBGE.',
            },
          ].map(f => (
            <div key={f.nome} className="border border-gov-border rounded p-4">
              <a href={f.url} target="_blank" rel="noreferrer" className="font-semibold text-gov-blue hover:underline">
                {f.nome}
              </a>
              <p className="text-gray-600 mt-1">{f.dados}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h2 className="section-title">Limitações</h2>
        <ul className="list-disc pl-5 text-sm text-gray-700 space-y-2">
          <li>Dados de vereadores municipais individuais não estão disponíveis via API nacional unificada.</li>
          <li>O IDHM mais recente disponível no IBGE é de 2010.</li>
          <li>Dados do SICONFI podem ter defasagem de até 1 ano.</li>
          <li>Contratos exibidos são apenas federais (convênios e contratos com a União).</li>
        </ul>
      </section>
    </div>
  );
}
