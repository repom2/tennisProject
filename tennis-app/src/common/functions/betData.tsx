import axios from "axios";
import {Bets} from "data/openapi";

interface BetsProps {
    level: string;
}

export async function getData({level}: BetsProps): Promise<{data: Bets[]}> {
    try {
        const response = await axios.get<Bets[]>("http://localhost:8000/tennisapi/bet-list/", {
            params: {
                level,
            },
            headers: {
                "Content-Type": "application/json",
            },
        });
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
