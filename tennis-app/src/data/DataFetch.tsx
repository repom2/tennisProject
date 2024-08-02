import {TennisApi} from "data/openapi";

const api = new TennisApi();

/**
 * Fetch information about players
 */
export const getPlayers = api.players.getPlayers.bind(api.players);

export const getEloRatings = api.players.getEloRatings.bind(api.players);

export const getBets = api.bets.getBets.bind(api.bets);

export const getPlayerStatistics = api.statistics.getPlayerStatistics.bind(api.statistics);

export const getFootballBets = api.bets.getFootballBets.bind(api.bets);
