import type { UserState } from '../store/user';

export async function createRecord(data: {
  firstName: string;
  lastName: string;
  instagram: string;
  referralSource: string;
  questionsAnswered: string;
  telegramID: string;
}) {
  const response = await fetch('/api/records', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      records: [{
        fields: {
          "First name": data.firstName,
          "Last Name": data.lastName,
          "Instagram": data.instagram,
          "Referral Source": data.referralSource,
          "Questions answered": data.questionsAnswered,
          "status": "pending",
          "telegramID": data.telegramID
        }
      }]
    })
  });

  if (!response.ok) {
    throw new Error('Failed to create record');
  }

  return response.json();
}

export async function uploadAttachment(recordId: string, file: Blob) {
  const formData = new FormData();
  formData.append('file', file, 'verification.jpg');
  formData.append('fileUrl', '');

  const response = await fetch(`/api/records/${recordId}/attachment`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('Upload failed:', errorData);
    throw new Error('Failed to upload attachment');
  }

  return response.json();
}
