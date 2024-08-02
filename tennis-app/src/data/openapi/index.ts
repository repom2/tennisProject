/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export { TennisApi } from './TennisApi';

export { ApiError } from './core/ApiError';
export { BaseHttpRequest } from './core/BaseHttpRequest';
export { CancelablePromise, CancelError } from './core/CancelablePromise';
export { OpenAPI } from './core/OpenAPI';
export type { OpenAPIConfig } from './core/OpenAPI';

export type { Bets } from './models/Bets';
export type { EloRatings } from './models/EloRatings';
export type { FootballBets } from './models/FootballBets';
export type { MatchProbabilities } from './models/MatchProbabilities';
export type { Players } from './models/Players';
export type { PlayerStatistics } from './models/PlayerStatistics';

export { BetsService } from './services/BetsService';
export { PlayersService } from './services/PlayersService';
export { StatisticsService } from './services/StatisticsService';
