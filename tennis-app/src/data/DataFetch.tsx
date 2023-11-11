import {TennisApi} from "data/openapi";

const api = new TennisApi();

/**
 * Fetch information about players
 */
export const getPlayers = api.players.getPlayers.bind(api.players);
