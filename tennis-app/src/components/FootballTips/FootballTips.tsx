import "./FootballTips.css";

import {getFootballData} from "common/functions/betFootballData";
import {FootballBets} from "data/openapi";
import React, {useState} from "react";
import {useQuery} from "react-query";

export const FootballTips: React.FC = () => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    const handleItemClick = (index: number) => {
        setOpenIndex(index === openIndex ? null : index);
    };
    const {isLoading, isError, data} = useQuery("football-bets", getFootballData);

    if (isLoading) return <div />;

    if (isError) return <div />;

    return (
        <div className="main">
            <table className="table">
                <thead>
                    <tr className="header">
                        <th>Match</th>
                        <th>Odds</th>
                        <th>Yield</th>
                        <th>Prob</th>
                        <th>Elo</th>
                        <th>EloHome</th>
                    </tr>
                </thead>
                <tbody>
                    {data &&
                        data.data &&
                        data.data.map((match: FootballBets, index: number) => (
                            <React.Fragment key={index}>
                                <tr
                                    key={match.matchId}
                                    className="row"
                                    onClick={() => handleItemClick(index)}
                                >
                                    <td>
                                        <div>{match.homeName}</div>
                                        <div>{match.awayName}</div>
                                    </td>
                                    <td>
                                        <div>{match.homeOdds}</div>
                                        <div>{match.drawOdds}</div>
                                        <div>{match.awayOdds}</div>
                                    </td>
                                    <td>
                                        <div>{match.homeYield}</div>
                                        <div>{match.drawYield}</div>
                                        <div>{match.awayYield}</div>
                                    </td>
                                    <td>{match.homeProb}</td>
                                    <td>{match.eloProb}</td>
                                    <td>{match.eloProbHome}</td>
                                </tr>
                                {openIndex === index && (
                                    <tr>
                                        <td colSpan={11}>
                                            {/* Whatever you want to display when clicked */}
                                            <div>{match.preview}</div>
                                            <div>{match.reasoning}</div>
                                        </td>
                                    </tr>
                                )}
                            </React.Fragment>
                        ))}
                </tbody>
            </table>
        </div>
    );
};
