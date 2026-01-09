import { LucideIcon, CheckCircle2 } from 'lucide-react';

interface ToolCardProps {
  icon: LucideIcon;
  iconBg: string;
  iconColor: string;
  title: string;
  description: string;
  features: string[];
  buttonColor: string;
  buttonHoverColor: string;
  href: string;
}

export default function ToolCard({
  icon: Icon,
  iconBg,
  iconColor,
  title,
  description,
  features,
  buttonColor,
  buttonHoverColor,
  href,
}: ToolCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl border-2 border-transparent hover:border-m4l-orange">
      <div className={`w-16 h-16 ${iconBg} rounded-lg flex items-center justify-center mb-6`}>
        <Icon className={`h-8 w-8 ${iconColor}`} />
      </div>
      
      <h4 className="text-xl font-bold text-m4l-blue mb-3">{title}</h4>
      
      <p className="text-gray-600 mb-6 leading-relaxed">{description}</p>
      
      <div className="space-y-2 mb-6">
        {features.map((feature, index) => (
          <div key={index} className="flex items-center text-sm text-gray-600">
            <CheckCircle2 className="h-4 w-4 text-m4l-orange mr-2 flex-shrink-0" />
            <span>{feature}</span>
          </div>
        ))}
      </div>
      
      <a
        href={href}
        className={`block w-full ${buttonColor} ${buttonHoverColor} text-white font-semibold py-3 rounded-lg transition duration-200 text-center`}
      >
        Launch Tool
      </a>
    </div>
  );
}
