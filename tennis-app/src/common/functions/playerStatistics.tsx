import axios from "axios";
import {PlayerStatistics} from "data/openapi";

interface PlayerStatsProps {
    level: string;
    playerId: string | null;
    surface: string | null;
}

export async function getPlayerStatistics({
    level,
    playerId,
    surface,
}: PlayerStatsProps): Promise<{data: PlayerStatistics[]}> {
    try {
        const response = await axios.get("http://localhost:8000/tennisapi/player-statistics/", {
            params: {
                level: level,
                playerId: playerId,
                surface: surface,
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
