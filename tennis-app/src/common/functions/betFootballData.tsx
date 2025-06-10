import axios from "axios";
import {FootballBets} from "data/openapi";

export async function getFootballData(): Promise<{data: FootballBets[]}> {
    try {
        const response = await axios.get<FootballBets[]>(
            "http://localhost:8000/tennisapi/football-bet-list/",
            {
                headers: {
                    "Content-Type": "application/json",
                },
            }
        );
        return response;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            throw new Error(
                `HTTP Error: ${error.response?.status || "unknown"} - ${error.message}`
            );
        }
        throw error;
    }
}
