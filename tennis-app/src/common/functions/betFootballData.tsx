import axios from "axios";
import {FootballBets} from "data/openapi";

export async function getFootballData(): Promise<{data: FootballBets[]}> {
    try {
        const response = await axios.get("http://localhost:8000/tennisapi/football-bet-list/", {
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
