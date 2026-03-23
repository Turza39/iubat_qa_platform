import Badge from '@/components/ui/Badge';
import { ShieldCheck } from 'lucide-react';

export default function VerificationBadge({ status }) {
  if (status === 'verified') {
    return (
      <Badge variant="verified" className="gap-1">
        <ShieldCheck size={11} />
        Verified Student
      </Badge>
    );
  }
  return null;
}