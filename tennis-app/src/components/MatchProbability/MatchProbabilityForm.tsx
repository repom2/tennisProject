import React, {useState} from "react";
import {useQuery} from "react-query";
import {getMatchProbabilities} from "common/functions/matchProbabilities";
import styles from "./MatchProbabilityForm.module.css";

interface MatchProbabilityFormProps {
    level?: string;
}

const MatchProbabilityForm: React.FC<MatchProbabilityFormProps> = ({level = "atp"}) => {
    const [formData, setFormData] = useState({
        tourName: "rome",
        homeSPW: 0.617,
        homeRPW: 0.416,
        awaySPW: 0.675,
        awayRPW: 0.364,
        surface: "hard",
        level: level,
    });

    const [shouldFetch, setShouldFetch] = useState(false);

    const {data, isLoading, isError} = useQuery(
        ["matchProbabilities", formData],
        () =>
            getMatchProbabilities({
                level: formData.level,
                tourName: formData.tourName,
                homeSPW: formData.homeSPW,
                homeRPW: formData.homeRPW,
                awaySPW: formData.awaySPW,
                awayRPW: formData.awayRPW,
                surface: formData.surface,
            }),
        {
            enabled: shouldFetch,
            onSettled: () => setShouldFetch(false),
        }
    );

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const {name, value} = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: name.includes("SPW") || name.includes("RPW") ? parseFloat(value) : value,
        }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setShouldFetch(true);
    };

    return (
        <div className={styles.container}>
            <h2>Match Probability Calculator</h2>
            
            <div className={styles.formResultsWrapper}>
                <form onSubmit={handleSubmit} className={styles.form}>
                <div className={styles.formGroup}>
                    <label htmlFor="level">Level:</label>
                    <select
                        id="level"
                        name="level"
                        value={formData.level}
                        onChange={handleChange}
                    >
                        <option value="atp">ATP</option>
                        <option value="wta">WTA</option>
                    </select>
                </div>

                <div className={styles.formGroup}>
                    <label htmlFor="tourName">Tournament:</label>
                    <input
                        type="text"
                        id="tourName"
                        name="tourName"
                        value={formData.tourName}
                        onChange={handleChange}
                    />
                </div>

                <div className={styles.formGroup}>
                    <label htmlFor="surface">Surface:</label>
                    <select
                        id="surface"
                        name="surface"
                        value={formData.surface}
                        onChange={handleChange}
                    >
                        <option value="hard">Hard</option>
                        <option value="clay">Clay</option>
                        <option value="grass">Grass</option>
                    </select>
                </div>

                <div className={styles.playerSection}>
                    <h3>Home Player</h3>
                    <div className={styles.formGroup}>
                        <label htmlFor="homeSPW">Service Points Won:</label>
                        <input
                            type="number"
                            id="homeSPW"
                            name="homeSPW"
                            step="0.001"
                            min="0"
                            max="1"
                            value={formData.homeSPW}
                            onChange={handleChange}
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="homeRPW">Return Points Won:</label>
                        <input
                            type="number"
                            id="homeRPW"
                            name="homeRPW"
                            step="0.001"
                            min="0"
                            max="1"
                            value={formData.homeRPW}
                            onChange={handleChange}
                        />
                    </div>
                </div>

                <div className={styles.playerSection}>
                    <h3>Away Player</h3>
                    <div className={styles.formGroup}>
                        <label htmlFor="awaySPW">Service Points Won:</label>
                        <input
                            type="number"
                            id="awaySPW"
                            name="awaySPW"
                            step="0.001"
                            min="0"
                            max="1"
                            value={formData.awaySPW}
                            onChange={handleChange}
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="awayRPW">Return Points Won:</label>
                        <input
                            type="number"
                            id="awayRPW"
                            name="awayRPW"
                            step="0.001"
                            min="0"
                            max="1"
                            value={formData.awayRPW}
                            onChange={handleChange}
                        />
                    </div>
                </div>

                    <button type="submit" className={styles.submitButton}>
                        Calculate Probabilities
                    </button>
                </form>

                {data && (
                    <div className={styles.results}>
                    <h3>Results</h3>
                    <div className={styles.resultGrid}>
                        <div className={styles.resultItem}>
                            <span>Match Probability:</span>
                            <span>{data.data.matchProb}</span>
                        </div>
                        <div className={styles.resultItem}>
                            <span>Event SPW:</span>
                            <span>{data.data.eventSPW}</span>
                        </div>
                        <div className={styles.resultItem}>
                            <span>Event RPW:</span>
                            <span>{data.data.eventRPW}</span>
                        </div>
                        <div className={styles.resultItem}>
                            <span>Games Over 21.5:</span>
                            <span>{data.data.gamesOver21_5}</span>
                        </div>
                        <div className={styles.resultItem}>
                            <span>Games Over 22.5:</span>
                            <span>{data.data.gamesOver22_5}</span>
                        </div>
                        <div className={styles.resultItem}>
                            <span>Games Over 23.5:</span>
                            <span>{data.data.gamesOver23_5}</span>
                        </div>
                        <div className={styles.resultItem}>
                            <span>Home AH 2.5:</span>
                            <span>{data.data.homeAH2_5}</span>
                        </div>
                        <div className={styles.resultItem}>
                            <span>Home AH 3.5:</span>
                            <span>{data.data.homeAH3_5}</span>
                        </div>
                        <div className={styles.resultItem}>
                            <span>Home AH 4.5:</span>
                            <span>{data.data.homeAH4_5}</span>
                        </div>
                    </div>
                </div>
                )}
            </div>
            
            {isLoading && <p className={styles.statusMessage}>Loading...</p>}
            {isError && <p className={styles.statusMessage}>Error fetching data</p>}
        </div>
    );
};

export default MatchProbabilityForm;
