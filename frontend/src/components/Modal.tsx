import React from 'react';
import './css/Modal.css';

interface ModalProps {
  title: string;
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const Modal: React.FC<ModalProps> = ({ title, isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close-button" onClick={onClose}>
          X
        </button>
        <h2 className="modal-title">{title}</h2>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
};

export default Modal;
