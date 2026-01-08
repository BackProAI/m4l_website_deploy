import Skeleton from './Skeleton';

export default function ToolCardSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6 hover:border-m4l-orange transition-colors">
      <div className="flex items-start gap-4 mb-4">
        <Skeleton className="h-12 w-12 rounded-lg" />
        <div className="flex-1">
          <Skeleton className="h-6 w-48 mb-2" />
          <Skeleton className="h-4 w-full mb-1" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </div>
      <Skeleton className="h-10 w-full rounded-lg" />
    </div>
  );
}
