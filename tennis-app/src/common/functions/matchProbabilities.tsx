import axios from "axios";
import {MatchProbabilities} from "data/openapi";

interface MatchProbabilitiesProps {
    tourName: string;
    homeSPW: number | null;
    awaySPW: number | null;
    homeRPW: number | null;
    awayRPW: number | null;
    surface: string | null;
}

export async function getMatchProbabilities({
    tourName,
    surface,
    homeSPW,
    awaySPW,
    homeRPW,
    awayRPW,
}: MatchProbabilitiesProps): Promise<{data: MatchProbabilities[]}> {
    try {
        const response = await axios.get("http://localhost:8000/tennisapi/match-probs/", {
            params: {
                tourName: tourName,
                surface: surface,
                homeSPW: homeSPW,
                awaySPW: awaySPW,
                homeRPW: homeRPW,
                awayRPW: awayRPW,
            },
            method: "get",
            headers: {
                "Content-Type": "application/json",
            },
        });
        return response;
    } catch (error) {
        if (error instanceof axios.AxiosError) {
            throw new Error(`HTTP ${error}`);
        }
        throw error;
    }
}
