export const EventType = {
  PROGRESS: "progress",
  FINAL: "final",
} as const;

export type EventType = (typeof EventType)[keyof typeof EventType];
