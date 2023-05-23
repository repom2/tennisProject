import {TennisAPI} from "data/openapi";

const api = new TennisAPI();

/**
 * Fetch information about players
 */
export const getPlayers = api.players.getPlayers.bind(api.players);
