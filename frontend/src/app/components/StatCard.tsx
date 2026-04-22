type StatCardProps = {
  title: string;
  value: string;
  subtext?: string;
};

export default function StatCard({ title, value, subtext }: StatCardProps) {
  return (
    <div className="bg-[#111111] border border-gray-800 rounded-2xl p-5 shadow-sm">
      <p className="text-sm text-gray-400">{title}</p>
      <h3 className="text-2xl font-bold text-white mt-2">{value}</h3>
      {subtext && <p className="text-sm text-gray-500 mt-1">{subtext}</p>}
    </div>
  );
}