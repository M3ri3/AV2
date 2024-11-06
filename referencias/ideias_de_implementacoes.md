# Bombeiros

## Tipos de Bombeiros
- **Terrestres**: Apaga só uma árvore por vez.
- **Helicóptero**: Apaga uma árvore e todos os seus vizinhos.

## Incendiário
- Acende uma árvore por vez (aleatória), pois é uma ação clandestina e não deixa rastros. Não pode ir numa área pegando fogo.

## Policial
- Persegue o incendiário.

## Chuva Aleatória
- Apaga uma árvore e suas três filhas vizinhas. A chuva acontece com uma probabilidade `p`.
- A água tem um volume fixo e chance de `X%` de apagar o fogo.

## Tempo de Vida da Árvore
- Dados sobre a duração da vida das árvores e como isso se relaciona com os incêndios.

## Cidades
- Alerta de Evacuação.
- Estratégia pros Bombeiros.

## Vento 
-se a direção do vento é de cima ou de baixo o fogo se propaga mais rápido nessa direção 

## Pontos de Incêndio Mais Intenso
Descrição: Algumas células podem ter um "hotspot", onde o fogo queima de forma mais intensa e se espalha com mais rapidez.
Implementação: Atribua uma probabilidade maior de espalhamento do fogo para algumas células aleatórias, como se fossem focos intensos de incêndio.

