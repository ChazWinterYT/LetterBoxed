import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import './css/Footer.css';

const Footer = () => {
  const { t } = useLanguage();

  return (
    <footer className="footer">
      <p>
        <a href="http://chazwinter.com">© 2024 chazwinter.com</a>
      </p>
      <p className="cookie-warning">
        {t('footer.cookieWarning')}
      </p>
    </footer>
  );
};

export default Footer;
