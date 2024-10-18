import {Box, TextField, Typography} from '@mui/material';
import React, {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from 'react';
import ReactMarkdown from 'react-markdown';
import styled from 'styled-components';

interface EditableMarkdownProps {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}

export const StyledReactMarkdown = styled(ReactMarkdown)`
  > *:first-child {
    margin-top: 0;
  }
  h1 {
    font-weight: 600;
    font-size: 1.2rem;
  }
  h2 {
    font-weight: 600;
    font-size: 1.15rem;
  }
  h3 {
    font-weight: 600;
    font-size: 1.1rem;
  }
  h4 {
    font-weight: 600;
    font-size: 1.05rem;
  }
  h5 {
    font-weight: 600;
    font-size: 1rem;
  }
  h6 {
    font-weight: 600;
    font-size: 1rem;
  }
`;

export const EditableMarkdown: React.FC<EditableMarkdownProps> = ({
  value,
  onChange,
  placeholder,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const textFieldRef = useRef<HTMLTextAreaElement>(null);

  const updateHeight = useCallback(() => {
    if (containerRef.current) {
      let newHeight: number;

      if (isEditing && textFieldRef.current) {
        // For editing mode, use scrollHeight of the textarea
        newHeight = textFieldRef.current.scrollHeight;
      } else if (!isEditing && contentRef.current) {
        // For viewing mode, get the rendered content height
        newHeight = contentRef.current.offsetHeight;
      } else {
        return; // Exit if we can't determine the height
      }

      newHeight -= 3;

      // Set a minimum height to prevent collapsing
      newHeight = Math.max(newHeight, 24);

      containerRef.current.style.height = `${newHeight}px`;
    }
  }, [isEditing]);

  useLayoutEffect(() => {
    // Use RAF to ensure DOM is fully updated before measuring
    requestAnimationFrame(() => {
      updateHeight();
    });

    const resizeObserver = new ResizeObserver(() => {
      requestAnimationFrame(() => {
        updateHeight();
      });
    });

    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    return () => resizeObserver.disconnect();
  }, [updateHeight]);

  const handleBlur = () => {
    setIsEditing(false);
    requestAnimationFrame(() => {
      updateHeight();
    });
  };

  const handleEdit = () => {
    setIsEditing(true);
    requestAnimationFrame(() => {
      updateHeight();
    });
  };

  useEffect(() => {
    requestAnimationFrame(() => {
      updateHeight();
    });
  }, [updateHeight, value]);

  return (
    <Box
      ref={containerRef}
      sx={{padding: '0px', transition: 'height 0.3s', flex: 1}}>
      {isEditing ? (
        <TextField
          fullWidth
          multiline
          value={value}
          onChange={e => {
            onChange(e.target.value);
          }}
          onBlur={handleBlur}
          placeholder={placeholder}
          autoFocus
          variant="outlined"
          inputRef={textFieldRef}
          sx={{
            '& .MuiOutlinedInput-root': {
              padding: 0,
              '& textarea': {
                padding: '0',
                overflow: 'hidden',
              },
            },
          }}
        />
      ) : (
        <Typography
          component="div"
          ref={contentRef}
          sx={{
            cursor: 'pointer',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
          onClick={handleEdit}>
          <StyledReactMarkdown>{value || placeholder}</StyledReactMarkdown>
        </Typography>
      )}
    </Box>
  );
};
