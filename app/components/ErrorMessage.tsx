type ErrorMessageProps = {
  message?: string;
};

export default function ErrorMessage({
  message = "Something went wrong. Please try again.",
}: ErrorMessageProps) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-5">
      <h2 className="font-semibold text-red-700">
        Unable to load data
      </h2>

      <p className="mt-2 text-sm text-red-600">
        {message}
      </p>
    </div>
  );
}