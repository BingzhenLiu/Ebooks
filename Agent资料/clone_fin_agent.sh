#!/bin/bash
for repo in \
  "https://github.com/yunduo0517mht/tianchi_AFAC_AGENT" \
  "https://github.com/virattt/ai-financial-agent" \
  "https://github.com/juanjuandog/FinSight-AI" \
  "https://github.com/hananedupouy/LLMs-in-Finance" \
  "https://github.com/pipiku915/FinMem-LLM-StockTrading" \
  "https://github.com/TauricResearch/TradingAgents"
do
  echo "Cloning $repo ..."
  git clone "$repo" || echo "⚠️  failed, skipping..."
done
echo "Done!"
