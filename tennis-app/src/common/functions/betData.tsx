import axios from "axios";
import {Bets} from "data/openapi";

interface BetsProps {
    level: string;
}

export async function getData({level}: BetsProps): Promise<{data: Bets[]}> {
    try {
        const response = await axios.get("http://localhost:8000/tennisapi/bet-list/", {
            params: {
                level: level,
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
