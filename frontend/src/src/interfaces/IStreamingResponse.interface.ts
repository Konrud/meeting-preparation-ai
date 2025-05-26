import type { EventType } from "../enums/EventType.enum";

export interface IStreamingResponse {
  type: EventType;
  data: {
    type: string;
    message: string;
  };
}
