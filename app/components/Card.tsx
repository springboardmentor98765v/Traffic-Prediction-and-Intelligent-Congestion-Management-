type CardProps = {
  title: string;
  value: string | number;
  valueClassName?: string;
};

export default function Card({
  title,
  value,
  valueClassName = "text-gray-800",
}: CardProps) {
  return (
    <div className="rounded-xl bg-white p-6 shadow">
      <h2 className="font-semibold text-gray-700">{title}</h2>

      <p className={`mt-3 text-xl font-bold ${valueClassName}`}>
        {value}
      </p>
    </div>
  );
}