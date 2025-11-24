import React, { useEffect } from "react";
import "./css/AdBanner.css";

interface AdBannerProps {
    /**
     * Google AdSense client ID (e.g., "ca-pub-XXXXXXXXXXXXXXXX")
     * Leave empty to disable ads
     */
    adClient?: string;
    /**
     * Google AdSense ad slot ID (e.g., "1234567890")
     * Leave empty to disable ads
     */
    adSlot?: string;
    /**
     * Ad format: "auto", "horizontal", "vertical", or "rectangle"
     */
    format?: "auto" | "horizontal" | "vertical" | "rectangle";
    /**
     * Whether to show ads (useful for development/testing)
     */
    enabled?: boolean;
}

const AdBanner: React.FC<AdBannerProps> = ({
    adClient,
    adSlot,
    format = "auto",
    enabled = true,
}) => {
    useEffect(() => {
        // Load Google AdSense script if not already loaded
        if (enabled && adClient && adSlot && typeof window !== "undefined") {
            const scriptId = "adsbygoogle-script";

            // Check if script already exists
            if (!document.getElementById(scriptId)) {
                const script = document.createElement("script");
                script.id = scriptId;
                script.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + adClient;
                script.async = true;
                script.crossOrigin = "anonymous";
                document.head.appendChild(script);
            }

            // Initialize the ad
            try {
                ((window as any).adsbygoogle = (window as any).adsbygoogle || []).push({});
            } catch (e) {
                console.error("Error initializing AdSense:", e);
            }
        }
    }, [enabled, adClient, adSlot]);

    // Don't render if ads are disabled or missing configuration
    if (!enabled || !adClient || !adSlot) {
        return null;
    }

    return (
        <div className="ad-banner-container">
            <ins
                className="adsbygoogle"
                style={{ display: "block" }}
                data-ad-client={adClient}
                data-ad-slot={adSlot}
                data-ad-format={format}
                data-full-width-responsive="true"
            />
        </div>
    );
};

export default AdBanner;

