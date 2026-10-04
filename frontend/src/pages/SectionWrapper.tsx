import React from 'react';
import { useParams } from 'react-router-dom';
import { DashboardPage } from './DashboardPage';

export const SectionWrapper: React.FC = () => {
  const { section } = useParams<{ section: string }>();
  return <DashboardPage section={section} />;
};
