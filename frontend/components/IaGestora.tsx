'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, AlertCircle, Loader2 } from 'lucide-react';

function renderMarkdown(text: string): React.ReactNode[] {
  const lines = text.split('\n');
  const nodes: React.ReactNode[] = [];

  const parseInline = (s: string, key: string): React.ReactNode => {
    // bold: **text**
    const parts = s.split(/(\*\*[^*]+\*\*)/g);
    return (
      <span key={key}>
        {parts.map((p, i) => {
          if (p.startsWith('**') && p.endsWith('**')) {
            return <strong key={i}>{p.slice(2, -2)}</strong>;
          }
          return p;
        })}
      </span>
    );
  };

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith('### ')) {
      nodes.push(<h3 key={i} className="text-sm font-bold text-gov-dark mt-3 mb-1 border-b border-gray-300 pb-0.5">{line.slice(4)}</h3>);
    } else if (line.startsWith('## ')) {
      nodes.push(<h2 key={i} className="text-base font-black text-gov-dark mt-3 mb-1">{line.slice(3)}</h2>);
    } else if (line.startsWith('# ')) {
      nodes.push(<h1 key={i} className="text-lg font-black text-gov-dark mt-3 mb-1">{line.slice(2)}</h1>);
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      nodes.push(<li key={i} className="ml-4 list-disc text-sm">{parseInline(line.slice(2), `li-${i}`)}</li>);
    } else if (line.trim() === '') {
      nodes.push(<br key={i} />);
    } else {
      nodes.push(<p key={i} className="text-sm leading-relaxed">{parseInline(line, `p-${i}`)}</p>);
    }
    i++;
  }
  return nodes;
}

interface IaGestoraProps {
  ibge: string;
  nomeMunicipio: string;
}

interface Mensagem {
  role: 'user' | 'assistant';
  content: string;
}

export default function IaGestora({ ibge, nomeMunicipio }: IaGestoraProps) {
  const [historico, setHistorico] = useState<Mensagem[]>([]);
  const [pergunta, setPergunta] = useState('');
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll para a última mensagem
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [historico, loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pergunta.trim() || loading) return;

    const novaPergunta = pergunta.trim();
    setPergunta('');
    setErro(null);

    const novoHistorico = [...historico, { role: 'user' as const, content: novaPergunta }];
    setHistorico(novoHistorico);
    setLoading(true);

    try {
      const res = await fetch(`/gestaobr/api/chat/${ibge}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pergunta: novaPergunta,
          historico: historico,
        }),
      });

      if (!res.ok) {
        if (res.status === 503) {
          throw new Error('Serviço de IA indisponível no momento. Tente novamente mais tarde.');
        }
        throw new Error('Erro ao processar a pergunta.');
      }

      const data = await res.json();
      
      setHistorico(prev => [...prev, { role: 'assistant', content: data.resposta }]);
    } catch (err: any) {
      setErro(err.message || 'Erro inesperado de comunicação com a IA.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col border border-gov-blue bg-white font-mono">
      {/* Corpo do chat */}
      <div 
        ref={scrollRef}
        className="h-[400px] overflow-y-auto p-4 flex flex-col gap-4 bg-gray-50"
      >
        {/* Mensagem Inicial */}
        <div className="flex gap-3 justify-start">
          <div className="w-8 h-8 rounded-full bg-gov-dark flex items-center justify-center shrink-0">
            <Bot size={16} className="text-white" />
          </div>
          <div className="bg-gray-100 text-gov-dark p-3 rounded-r-lg rounded-bl-lg max-w-[85%] text-sm whitespace-pre-wrap">
            Olá! Sou a IA Gestora de {nomeMunicipio}. Posso responder perguntas sobre indicadores, orçamento, saúde, educação e outros dados do município. Como posso ajudar?
          </div>
        </div>

        {historico.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-gov-dark flex items-center justify-center shrink-0">
                <Bot size={16} className="text-white" />
              </div>
            )}
            
            <div className={`p-3 max-w-[85%] ${
              msg.role === 'user' 
                ? 'bg-gov-blue text-white rounded-l-lg rounded-br-lg text-sm' 
                : 'bg-gray-100 text-gov-dark rounded-r-lg rounded-bl-lg'
            }`}>
              {msg.role === 'assistant' ? renderMarkdown(msg.content) : msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 justify-start">
             <div className="w-8 h-8 rounded-full bg-gov-dark flex items-center justify-center shrink-0">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-gray-100 text-gov-dark p-3 rounded-r-lg rounded-bl-lg flex items-center gap-2">
              <Loader2 size={16} className="animate-spin text-gov-blue" />
              <span className="text-xs">Processando...</span>
            </div>
          </div>
        )}

        {erro && (
          <div className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded border border-red-200 text-xs my-2">
            <AlertCircle size={16} />
            {erro}
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t border-gov-blue p-3 bg-white flex gap-2">
        <input
          type="text"
          value={pergunta}
          onChange={(e) => setPergunta(e.target.value)}
          placeholder={`Pergunte sobre ${nomeMunicipio}...`}
          className="flex-1 border border-gray-300 p-2 text-sm focus:outline-none focus:border-gov-blue focus:ring-1 focus:ring-gov-blue"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !pergunta.trim()}
          className="bg-gov-blue text-white p-2 px-4 hover:bg-blue-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}