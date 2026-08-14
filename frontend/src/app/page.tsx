import Navbar from "@/components/Navbar";
import MarketTicker from "@/components/MarketTicker";
import Hero from "@/components/Hero";
import MarketsPreview from "@/components/MarketsPreview";
import BuySell from "@/components/BuySell";
import Features from "@/components/Features";
import Products from "@/components/Products";
import Security from "@/components/Security";
import CTA from "@/components/CTA";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#070b14]">
      <Navbar />
      <MarketTicker />
      <Hero />
      <MarketsPreview />
      <BuySell />
      <Features />
      <Products />
      <Security />
      <CTA />
      <Footer />
    </main>
  );
}
