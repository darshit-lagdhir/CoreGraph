import { useCallback } from 'react';

/**
 * useClusterColors: Dynamic chromatic grouping engine for the WebGL viewport.
 *
 * Utilizing the Golden Angle (137.5 degrees) to ensure maximum visual
 * distinction between adjacent community IDs.
 */
export const useClusterColors = () => {
    const getClusterColor = useCallback((clusterId: number, communityRisk: number = 0) => {
        if (clusterId === undefined || clusterId === null) {
            return '#4f4f4f'; // Default neutral for orphan nodes
        }

        // 1. Hue Selection: Golden Angle distribution for topological segmentation
        const hue = (clusterId * 137.5) % 360;

        // 2. Saturation: Locked at 70% for vibrant OSINT HUD aesthetics
        const saturation = 70;

        // 3. Lightness: Dynamic mapping based on Community Risk Score (CVI)
        // High risk clusters are rendered brighter/more intense in the HUD
        const lightness = 50 + (communityRisk * 20); // range 50-70%

        return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    }, []);

    return { getClusterColor };
};
