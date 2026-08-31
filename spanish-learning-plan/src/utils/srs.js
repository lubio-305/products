// 簡化版 Leitner box 間隔複習系統
import { addDays, todayISO } from './dates'

export const BOX_INTERVALS = [1, 2, 4, 8, 16, 30]
export const MAX_BOX = BOX_INTERVALS.length - 1

export function initCardState(card) {
  return {
    ...card,
    box: 0,
    nextReview: todayISO(),
    reviews: 0,
    correct: 0,
  }
}

export function isDue(card, todayIso = todayISO()) {
  return !card.nextReview || card.nextReview <= todayIso
}

export function reviewCard(card, remembered, todayIso = todayISO()) {
  const box = remembered ? Math.min(card.box + 1, MAX_BOX) : 0
  const interval = BOX_INTERVALS[box]
  return {
    ...card,
    box,
    nextReview: addDays(todayIso, interval),
    reviews: (card.reviews || 0) + 1,
    correct: (card.correct || 0) + (remembered ? 1 : 0),
  }
}

export function dueCards(cards, todayIso = todayISO()) {
  return cards.filter((c) => isDue(c, todayIso))
}
