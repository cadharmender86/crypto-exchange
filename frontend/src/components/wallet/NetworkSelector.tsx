interface NetworkSelectorProps {
  networks: string[];
  value: string;
  onChange: (network: string) => void;
}

export default function NetworkSelector({
  networks,
  value,
  onChange,
}: NetworkSelectorProps) {
  return (
    <div>
      <label className="mb-2 block text-sm text-gray-400">Network</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-gray-700 bg-gray-900 p-3"
      >
        {networks.map((network) => (
          <option key={network}>{network}</option>
        ))}
      </select>
    </div>
  );
}
