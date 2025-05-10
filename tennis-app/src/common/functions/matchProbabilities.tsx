import axios from "axios";
import {MatchProbabilities} from "data/openapi";

interface MatchProbabilitiesProps {
    tourName?: string;
    matchId?: string;
    homeSPW?: number | null;
    awaySPW?: number | null;
    homeRPW?: number | null;
    awayRPW?: number | null;
    surface?: string | null;
    level?: string;
}

export async function getMatchProbabilities({
    matchId,
    tourName,
    surface,
    homeSPW,
    awaySPW,
    homeRPW,
    awayRPW,
    level,
}: MatchProbabilitiesProps): Promise<{data: MatchProbabilities}> {
    try {
        const response = await axios.get<MatchProbabilities>("http://localhost:8000/tennisapi/match-probs/", {
            params: {
                tourName,
                surface,
                homeSPW,
                awaySPW,
                homeRPW,
                awayRPW,
                level,
            },
            headers: {
                "Content-Type": "application/json",
            },
        });
        return response;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            throw new Error(`HTTP Error: ${error.response?.status || 'unknown'} - ${error.message}`);
        }
        throw error;
    }
}
