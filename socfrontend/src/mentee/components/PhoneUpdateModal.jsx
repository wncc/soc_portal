// PhoneUpdateModal.jsx
import { useState } from 'react';
import api from '../../utils/api';

const PhoneUpdateModal = ({ onClose }) => {
  const [phone, setPhone] = useState('');
  const role = localStorage.getItem('role');

  const handleSubmit = async (e) => {
    e.preventDefault();
    onClose();
    try {
      if (role === 'mentor') {
        await api.patch(`https://socb.tech-iitb.org/api/projects/mentor/profile/`, {
          phone_number: phone,
        });
      } else if (role === 'mentee') {
        await api.patch(`https://socb.tech-iitb.org/api/projects/mentee/profile/`, {
          phone_number: phone,
        });
      } else {
        alert('Invalid role. Please login again.');
        localStorage.removeItem('authToken');
        return;
      }

      alert('Phone number updated successfully!');
       // Close the modal after success
    } catch (error) {
      console.error('Failed to update phone number:', error);
      alert('Failed to update phone number. Try again.');
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-6 rounded shadow-md w-96">
        <h2 className="text-2xl font-semibold mb-4">Phone Number</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Enter your phone number"
            className="w-full p-2 mb-4 border border-gray-300 rounded"
            required
            pattern="[0-9]{10}" // enforce 10 digits
            title="Phone number must be 10 digits"
          />
          <div className="flex justify-between">
            <button
              type="submit"
              className="bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700"
            >
              Update
            </button>
            
          </div>
        </form>
      </div>
    </div>
  );
};

export default PhoneUpdateModal;
